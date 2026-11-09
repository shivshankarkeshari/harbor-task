"""Independent browser/state acceptance checks for original Field Desk."""
import csv
from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import re
import socket
import sqlite3
import subprocess
import tempfile
import time
import traceback
import urllib.request
import urllib.error

from playwright.sync_api import sync_playwright, expect
from grade import PLAN,CRITICAL,grade

LOG=Path('/logs/verifier');LOG.mkdir(parents=True,exist_ok=True)
APP=Path('/app');HERE=Path(__file__).parent
CAT={code:json.loads((HERE/'catalogs'/f'{code}.json').read_text()) for code in ['en','de','ar']}
CHECKS={};EXPECTED=PLAN;BROWSER=None;ACTIVE_CASE=None;SCREENSHOT_WARNINGS={}


def normalized(text):
    text=text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩٬٫','0123456789,.'))
    return re.sub(r'\s+',' ',re.sub('[\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069]','',text)).strip()


def message(page,locale,key,**args):
    text=CAT[locale][key]
    if isinstance(text,dict):
        count=args['count']
        if locale=='ar':
            plural='zero' if count==0 else 'one' if count==1 else 'two' if count==2 else 'few' if 3<=count%100<=10 else 'many' if 11<=count%100<=99 else 'other'
        else:plural='one' if count==1 else 'other'
        text=text.get(plural,text['other'])
    for key,value in args.items():
        if type(value) in [int,float]:value=page.evaluate('([locale,n])=>new Intl.NumberFormat(locale).format(n)',[locale,value])
        text=text.replace('{'+key+'}',str(value))
    return text


def eventually(page,predicate,description):
    deadline=time.monotonic()+3
    last=None
    while time.monotonic()<deadline:
        try:
            result=predicate()
            if result:return
            last=result
        except Exception as error:last=str(error)
        page.wait_for_timeout(40)
    raise AssertionError(description+'; last observation: '+str(last))


def text_is(page,locator,expected):
    eventually(page,lambda:normalized(locator.inner_text(timeout=500))==normalized(expected),f'Expected visible text {expected!r}')


def has_copy(page,key,locale,**args):
    expected=message(page,locale,key,**args)
    eventually(page,lambda:normalized(expected) in normalized(page.locator('body').inner_text()),f'Missing UI copy {key}: {expected!r}')


def labelled(page,testid,key,locale):
    expected=message(page,locale,key)
    locator=page.get_by_test_id(testid)
    def observed():
        return locator.evaluate('''el=>{
          if(el.getAttribute('aria-label'))return el.getAttribute('aria-label');
          if(el.getAttribute('aria-labelledby'))return document.getElementById(el.getAttribute('aria-labelledby'))?.textContent;
          return [...(el.labels||[])].map(label=>{const copy=label.cloneNode(true);copy.querySelectorAll('input,select,textarea').forEach(x=>x.remove());return copy.textContent}).join(' ');
        }''')
    eventually(page,lambda:normalized(observed() or '')==normalized(expected),f'Wrong accessible label for {testid}: expected {expected!r}')


class Server:
    def __init__(self,name):
        self.data=Path(tempfile.mkdtemp(prefix='field-desk-'+name+'-',dir='/tmp'))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));self.port=sock.getsockname()[1]
        self.url=f'http://127.0.0.1:{self.port}'
        self.log=(LOG/(name+'-server.log')).open('w')
        self.process=subprocess.Popen(['python','/app/serve.py','--port',str(self.port),'--data',str(self.data)],stdout=self.log,stderr=subprocess.STDOUT)
        for _ in range(100):
            try:
                with urllib.request.urlopen(self.url+'/healthz',timeout=.5):return
            except OSError:time.sleep(.05)
        raise RuntimeError('Application server did not start')

    def call(self,path,body=None,operator='robin'):
        request=urllib.request.Request(self.url+'/api/'+path,data=json.dumps(body).encode() if body is not None else None,
            headers={'Content-Type':'application/json','X-Operator':operator})
        try:response=urllib.request.urlopen(request,timeout=5)
        except urllib.error.HTTPError as error:response=error
        with response:
            data=response.read()
            return response.code,json.loads(data) if 'json' in response.headers.get('Content-Type','') else data.decode()

    def bootstrap(self,operator='robin'):return self.call('bootstrap?operator='+operator)[1]

    def stop(self):
        self.process.terminate()
        try:self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.log.close()


@contextmanager
def scene(name):
    server=Server(name);context=BROWSER.new_context(viewport={'width':1280,'height':900},permissions=['clipboard-read','clipboard-write'])
    page=context.new_page();page.set_default_timeout(2000)
    try:
        page.goto(server.url)
        expect(page.get_by_test_id('language')).to_be_visible(timeout=6000)
        yield page,server
        if ACTIVE_CASE and ACTIVE_CASE.startswith('view_'):
            try:
                page.screenshot(path=str(LOG/(ACTIVE_CASE+'.png')),full_page=True)
                (LOG/(ACTIVE_CASE+'-visible.txt')).write_text(page.locator('body').inner_text(timeout=500))
            except Exception as error:
                SCREENSHOT_WARNINGS[ACTIVE_CASE]=str(error)
    except Exception:
        try:
            prefix=ACTIVE_CASE or name
            page.screenshot(path=str(LOG/(prefix+'.png')),full_page=True)
            (LOG/(prefix+'-visible.txt')).write_text(page.locator('body').inner_text(timeout=500))
            fields=page.locator('input,textarea,select').evaluate_all('elements=>elements.map(element=>({id:element.id,value:element.value,checked:element.checked}))')
            (LOG/(prefix+'-state.json')).write_text(json.dumps({'locale':page.locator('html').get_attribute('lang'),'fields':fields,'persisted':server.bootstrap()},indent=2,ensure_ascii=False)+'\n')
        except Exception:pass
        raise
    finally:context.close();server.stop()


def check(name,category,function):
    global ACTIVE_CASE
    assert PLAN[name]==category, 'Acceptance-plan mismatch'
    ACTIVE_CASE=name
    try:
        function();CHECKS[name]={'passed':True,'category':category,'critical':name in CRITICAL};print('PASS '+name,flush=True)
    except Exception as error:
        CHECKS[name]={'passed':False,'category':category,'critical':name in CRITICAL,'error':str(error),'traceback':traceback.format_exc()}
        CHECKS[name]['evidence']=[path.name for path in [LOG/(name+'.png'),LOG/(name+'-visible.txt'),LOG/(name+'-state.json')] if path.is_file()]
        print('FAIL '+name+': '+str(error),flush=True)
    finally:ACTIVE_CASE=None


def language(page,locale):
    # Native user interaction blurs the previous field before changing a select.
    selector=page.get_by_test_id('language')
    selector.focus();selector.select_option(locale)
    expect(page.locator('html')).to_have_attribute('lang',locale,timeout=4000)


def visit(page,route):
    page.get_by_test_id('nav-'+route).click()
    expect(page).to_have_url(re.compile('#'+route+'$'))


def dialog(page,kind):
    if kind=='new-order':page.get_by_test_id('new-order').click()
    elif kind=='edit-order':page.get_by_test_id('edit-1').click()
    elif kind=='bulk':page.get_by_test_id('select-1').check();page.get_by_test_id('bulk').click()
    elif kind=='assign':visit(page,'dispatch');page.get_by_test_id('assign-1').click()
    elif kind=='reserve':visit(page,'parts');page.get_by_test_id('reserve-1').click()
    elif kind=='charge':visit(page,'billing');page.get_by_test_id('charge').click()
    elif kind=='export':visit(page,'reports');page.get_by_test_id('export').click()
    expect(page.get_by_role('dialog')).to_be_visible()


PAGES={
 'orders':['orders.title','orders.subtitle','orders.search','orders.filter','orders.all','orders.new','orders.complete','field.title','field.customer','field.status','field.budget','field.actions','orders.choose','orders.edit'],
 'dispatch':['dispatch.title','dispatch.subtitle','dispatch.available','dispatch.unavailable','dispatch.assign'],
 'parts':['parts.title','parts.subtitle','parts.reserve'],
 'billing':['billing.title','billing.subtitle','billing.record','billing.total','billing.empty'],
 'activity':['activity.title','activity.subtitle'],
 'reports':['reports.title','reports.subtitle','reports.open','reports.budget','reports.export','reports.exportNote'],
 'settings':['settings.title','settings.subtitle','settings.notifications','settings.notificationsHint','common.save'],
 'help':['help.title','help.subtitle','help.orders','help.dispatch','help.parts','help.billing','help.export','help.copy'],
}
TITLES={'new-order':'order.createTitle','edit-order':'order.editTitle','bulk':'bulk.title','assign':'dispatch.dialogTitle','reserve':'parts.dialogTitle','charge':'billing.dialogTitle','export':'reports.dialogTitle'}


def main():
    global BROWSER
    for code in CAT:
        supplied=json.loads((APP/'static/locales'/f'{code}.json').read_text())
        assert all(supplied.get(key)==value for key,value in CAT[code].items()),f'Approved {code} catalog changed'
    with sync_playwright() as playwright:
        BROWSER=playwright.chromium.launch(headless=True,args=['--no-sandbox'])
        def api_contracts():
            with scene('api-contracts') as (page,server):
                before=server.bootstrap()
                assert len(before['orders'])==12 and [row['stock'] for row in before['parts']]==[4,0,1,2,11,102]
                for locale in ['en','de','ar']:
                    server.call('preferences',{'locale':locale,'notifications':True})
                    code,result=server.call('assign',{'order_id':1,'crew_id':2})
                    assert code==400 and result=={'ok':False,'error':{'code':'CREW_UNAVAILABLE','message':'The selected crew is unavailable.'}}
                    code,result=server.call('order',{'title':'','budget_minor':0})
                    assert code==400 and result['error']['code']=='TITLE_REQUIRED' and result['error']['message']=='A work-order title is required.'
                assert server.bootstrap()['orders']==before['orders']
        check('machine_api_contracts','constraint_satisfaction',api_contracts)

        for locale in ['en','de','ar']:
            for route,keys in PAGES.items():
                def page_case(locale=locale,route=route,keys=keys):
                    with scene('page-'+route+'-'+locale) as (page,server):
                        language(page,locale);visit(page,route)
                        for key in ['app.operator','app.language',*['nav.'+name for name in PAGES],*keys]:has_copy(page,key,locale)
                        text_is(page,page.get_by_test_id('page-title'),message(page,locale,keys[0]))
                        for name in PAGES:text_is(page,page.get_by_test_id('nav-'+name),message(page,locale,'nav.'+name))
                        labelled(page,'operator','app.operator',locale);labelled(page,'language','app.language',locale)
                        if route=='orders':
                            labelled(page,'search','orders.search',locale);labelled(page,'filter','orders.filter',locale)
                            expect(page.get_by_test_id('search')).to_have_attribute('placeholder',CAT[locale]['orders.searchHint'])
                            expect(page.get_by_test_id('select-1')).to_have_attribute('aria-label',message(page,locale,'orders.selectOne',title='Ready for pickup'))
                            text_is(page,page.get_by_test_id('new-order'),message(page,locale,'orders.new'))
                            text_is(page,page.get_by_test_id('bulk'),message(page,locale,'orders.complete'))
                            text_is(page,page.get_by_test_id('edit-1'),message(page,locale,'orders.edit'))
                            text_is(page,page.get_by_test_id('status-1'),message(page,locale,'status.OPEN'))
                            text_is(page,page.get_by_test_id('status-3'),message(page,locale,'status.ASSIGNED'))
                            headers=['orders.choose','field.title','field.customer','field.status','field.budget','field.actions']
                            for i,key in enumerate(headers):text_is(page,page.locator('th').nth(i),message(page,locale,key))
                        if route=='dispatch':
                            text_is(page,page.get_by_test_id('crew-1-status'),message(page,locale,'dispatch.available'))
                            text_is(page,page.get_by_test_id('crew-2-status'),message(page,locale,'dispatch.unavailable'))
                        if route=='activity':text_is(page,page.get_by_test_id('event-1'),message(page,locale,'event.opened',actor='Robin',title='Ready for pickup'))
                        if route=='settings':text_is(page,page.get_by_test_id('settings-operator'),message(page,locale,'settings.operatorNote',name='Robin'))
                check('view_'+route+'_'+locale,'artifact_quality',page_case)

            for kind,title in TITLES.items():
                def dialog_case(locale=locale,kind=kind,title=title):
                    with scene('dialog-'+kind+'-'+locale) as (page,server):
                        language(page,locale);dialog(page,kind)
                        text_is(page,page.get_by_test_id('dialog-title'),message(page,locale,title))
                        for key in ['common.cancel','common.confirm']:has_copy(page,key,locale)
                        text_is(page,page.get_by_test_id('cancel'),message(page,locale,'common.cancel'))
                        text_is(page,page.get_by_test_id('submit'),message(page,locale,'common.confirm'))
                        expect(page.get_by_test_id('dialog-x')).to_have_attribute('aria-label',CAT[locale]['common.close'])
                        if kind in ['new-order','edit-order']:
                            for id,key in [('title','field.title'),('customer','field.customer'),('budget','field.budget')]:labelled(page,id,key,locale)
                            expect(page.get_by_test_id('title')).to_have_attribute('placeholder',CAT[locale]['order.titleHint'])
                            has_copy(page,'order.amountHint',locale)
                        if kind=='assign':labelled(page,'order-id','field.order',locale)
                        if kind=='reserve':labelled(page,'units','parts.quantity',locale);has_copy(page,'parts.hint',locale)
                        if kind=='charge':
                            for id,key in [('order-id','field.order'),('amount','billing.amount'),('memo','billing.memo')]:labelled(page,id,key,locale)
                            expect(page.get_by_test_id('memo')).to_have_attribute('placeholder',CAT[locale]['billing.memoHint'])
                        if kind=='export':has_copy(page,'reports.dialogBody',locale)
                        page.get_by_test_id('cancel').click();expect(page.get_by_role('dialog')).to_have_count(0)
                check('dialog_'+kind+'_'+locale,'artifact_quality',dialog_case)

            def errors(locale=locale):
                with scene('errors-'+locale) as (page,server):
                    language(page,locale);dialog(page,'new-order');page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.TITLE_REQUIRED'))
                    page.get_by_test_id('title').fill('Untouched customer text');page.get_by_test_id('budget').fill('invalid');page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.AMOUNT_INVALID'))
                    page.get_by_test_id('cancel').click();visit(page,'dispatch');page.get_by_test_id('assign-2').click();page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.CREW_UNAVAILABLE'))
                    page.get_by_test_id('cancel').click();visit(page,'parts');page.get_by_test_id('reserve-1').click();page.get_by_test_id('units').fill('9');page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.PARTS_SHORT',available=4))
                    page.get_by_test_id('units').fill('0');page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.QUANTITY_INVALID'))
                    page.get_by_test_id('cancel').click();visit(page,'orders');page.get_by_test_id('bulk').click();page.get_by_test_id('submit').click()
                    text_is(page,page.get_by_test_id('dialog-error'),message(page,locale,'error.SELECTION_REQUIRED'))
                    assert len(server.bootstrap()['orders'])==12
            check('validation_and_server_errors_'+locale,'functional_correctness',errors)

            def stock_plurals(locale=locale):
                with scene('stock-'+locale) as (page,server):
                    language(page,locale);visit(page,'parts')
                    for part in server.bootstrap()['parts']:
                        text_is(page,page.get_by_test_id('stock-'+str(part['id'])),message(page,locale,'parts.stock',count=part['stock']))
            check('quantity_plural_forms_'+locale,'functional_correctness',stock_plurals)

            def bulk_flow(locale=locale):
                with scene('bulk-'+locale) as (page,server):
                    language(page,locale)
                    for count in [0,1,2,3,11]:
                        for i in range(1,13):page.get_by_test_id('select-'+str(i)).set_checked(i<=count)
                        text_is(page,page.get_by_test_id('selection-count'),message(page,locale,'orders.selected',count=count))
                    page.get_by_test_id('bulk').click();text_is(page,page.get_by_test_id('bulk-question'),message(page,locale,'bulk.question',count=11));page.get_by_test_id('submit').click()
                    expect(page.get_by_role('dialog')).to_have_count(0)
                    text_is(page,page.locator('#toast'),message(page,locale,'notice.completed',count=11))
                    eventually(page,lambda:sum(row['status']=='DONE' for row in server.bootstrap()['orders'])==11,'Bulk action did not persist DONE codes')
                    visit(page,'activity');has_copy(page,'event.completed',locale,actor='Robin',count=11)
                    visit(page,'reports');text_is(page,page.get_by_test_id('open-count'),message(page,locale,'reports.count',count=1))
            check('bulk_workflow_'+locale,'functional_correctness',bulk_flow)

            def money_flow(locale=locale):
                with scene('money-'+locale) as (page,server):
                    language(page,locale);dialog(page,'charge')
                    sample={'en':'1,234.50','de':'1.234,50','ar':'١٬٢٣٤٫٥٠'}[locale]
                    page.get_by_test_id('amount').fill(sample);page.get_by_test_id('memo').fill('Ready for pickup; Keep original العربية');page.get_by_test_id('submit').click()
                    expect(page.get_by_role('dialog')).to_have_count(0)
                    eventually(page,lambda:len(server.bootstrap()['charges'])==1,'Charge not persisted')
                    charge=server.bootstrap()['charges'][0]
                    assert charge['amount_minor']==123450 and charge['memo']=='Ready for pickup; Keep original العربية',charge
                    expected=page.evaluate('locale=>new Intl.NumberFormat(locale,{style:"currency",currency:"EUR"}).format(1234.5)',locale)
                    text_is(page,page.get_by_test_id('charge-total'),expected)
                    text_is(page,page.locator('#toast'),message(page,locale,'notice.charged'))
            check('money_and_memo_'+locale,'functional_correctness',money_flow)

            def csv_flow(locale=locale):
                with scene('export-'+locale) as (page,server):
                    language(page,locale);before=server.bootstrap()['orders'];visit(page,'reports');page.get_by_test_id('export').click()
                    with page.expect_download() as info:page.get_by_test_id('submit').click()
                    download=info.value;assert download.suggested_filename=='work-orders.csv'
                    rows=list(csv.DictReader(Path(download.path()).read_text().splitlines()))
                    assert list(rows[0])==['order_id','title','status','budget_minor','crew_id']
                    assert len(rows)==12
                    for row,original in zip(rows,before):
                        assert row['title']==original['title'] and row['status']==original['status'] and row['budget_minor']==str(original['budget_minor'])
                    text_is(page,page.locator('#toast'),message(page,locale,'notice.exported'))
            check('csv_contract_'+locale,'constraint_satisfaction',csv_flow)

            def empty_help(locale=locale):
                with scene('empty-help-'+locale) as (page,server):
                    language(page,locale);page.get_by_test_id('search').fill('no-such-customer-937')
                    for key in ['orders.emptyTitle','orders.emptyBody','common.clear']:has_copy(page,key,locale)
                    page.get_by_test_id('clear-search').click();expect(page.get_by_test_id('order-1')).to_be_visible()
                    assert 'Ready for pickup' in page.get_by_test_id('order-1').inner_text()
                    visit(page,'help');page.get_by_test_id('copy-help').click();text_is(page,page.get_by_test_id('help-copy-result'),message(page,locale,'common.copied'))
                    clipboard=page.evaluate('()=>navigator.clipboard.readText()');assert clipboard==CAT[locale]['help.copyText']
            check('empty_search_and_help_'+locale,'artifact_quality',empty_help)

        def live_draft():
            with scene('live-draft') as (page,server):
                language(page,'de');page.get_by_test_id('search').fill('Ready');page.get_by_test_id('filter').select_option('OPEN');page.get_by_test_id('select-1').check();dialog(page,'edit-order')
                page.get_by_test_id('title').fill('Open House: keep this wording');page.get_by_test_id('customer').fill('Ready for pickup');page.get_by_test_id('budget').fill('1.234,50')
                # Hold only a successful preferences response. The still-enabled
                # draft may be edited while a real language-keyboard action saves.
                pending=[]
                def hold_preference_response(route):
                    if route.request.post_data_json.get('locale')=='ar':
                        pending.append((route,route.fetch()))
                    else:route.continue_()
                page.route('**/api/preferences',hold_preference_response)
                page.get_by_test_id('language').focus();page.get_by_test_id('language').press('End')
                eventually(page,lambda:bool(pending),'Language preference request was not issued')
                current=page.locator('html').get_attribute('lang')
                page.get_by_test_id('budget').fill({'de':'1.234,51','ar':'١٢٣٤٫٥١','en':'1,234.51'}[current])
                route,response=pending.pop(0);assert response.status==200
                route.fulfill(response=response)
                expect(page.locator('html')).to_have_attribute('lang','ar')
                text_is(page,page.get_by_test_id('dialog-title'),message(page,'ar','order.editTitle'))
                expect(page.get_by_test_id('title')).to_have_value('Open House: keep this wording');expect(page.get_by_test_id('customer')).to_have_value('Ready for pickup')
                page.get_by_test_id('submit').click();expect(page.get_by_role('dialog')).to_have_count(0)
                order=server.bootstrap()['orders'][0];assert order['budget_minor']==123451 and order['title']=='Open House: keep this wording',order
                expect(page.get_by_test_id('search')).to_have_value('Ready');expect(page.get_by_test_id('filter')).to_have_value('OPEN')
                text_is(page,page.get_by_test_id('selection-count'),message(page,'ar','orders.selected',count=1))
                text_is(page,page.locator('#toast'),message(page,'ar','notice.saved',title=order['title']))
                language(page,'de');text_is(page,page.locator('#toast'),message(page,'de','notice.saved',title=order['title']))
        check('live_draft_numeric_meaning_and_view_state','robustness',live_draft)

        def live_errors():
            with scene('live-errors') as (page,server):
                dialog(page,'new-order');page.get_by_test_id('submit').click()
                text_is(page,page.get_by_test_id('dialog-error'),message(page,'en','error.TITLE_REQUIRED'))
                language(page,'de');text_is(page,page.get_by_test_id('dialog-error'),message(page,'de','error.TITLE_REQUIRED'))
                language(page,'ar');text_is(page,page.get_by_test_id('dialog-error'),message(page,'ar','error.TITLE_REQUIRED'))
                page.get_by_test_id('cancel').click();page.get_by_test_id('select-1').check();page.get_by_test_id('select-2').check();page.get_by_test_id('bulk').click()
                text_is(page,page.get_by_test_id('bulk-question'),message(page,'ar','bulk.question',count=2))
                language(page,'de');text_is(page,page.get_by_test_id('bulk-question'),message(page,'de','bulk.question',count=2))
        check('live_error_and_confirmation_retranslation','robustness',live_errors)

        def preferences():
            with scene('preferences') as (page,server):
                language(page,'ar');page.reload();expect(page.locator('html')).to_have_attribute('lang','ar');has_copy(page,'orders.title','ar')
                page.get_by_test_id('operator').select_option('amal');expect(page.locator('html')).to_have_attribute('lang','de');has_copy(page,'orders.title','de')
                visit(page,'settings');expect(page.get_by_test_id('notifications')).not_to_be_checked()
                language(page,'en');expect(page.get_by_test_id('notifications')).not_to_be_checked()
                assert server.bootstrap('amal')['preferences']=={'operator':'amal','locale':'en','notifications':0}
                page.get_by_test_id('operator').select_option('robin');expect(page.locator('html')).to_have_attribute('lang','ar')
                expect(page.get_by_test_id('notifications')).to_be_checked();page.reload();expect(page.locator('html')).to_have_attribute('lang','ar')
                assert server.bootstrap('robin')['preferences']['locale']=='ar'
        check('operator_locale_persistence_and_preference_isolation','constraint_satisfaction',preferences)

        def rtl():
            with scene('rtl') as (page,server):
                for locale in ['ar','de','en']:
                    language(page,locale);expect(page.locator('html')).to_have_attribute('dir','rtl' if locale=='ar' else 'ltr')
                    nav=page.locator('#navigation').bounding_box();main=page.locator('#main').bounding_box()
                    assert nav['x']>main['x'] if locale=='ar' else nav['x']<main['x'],(locale,nav,main)
                page.screenshot(path=str(LOG/'layout-example.png'),full_page=True)
        check('rtl_navigation_layout','artifact_quality',rtl)

        def reserve_digits():
            with scene('reserve-digits') as (page,server):
                language(page,'ar');visit(page,'parts');page.get_by_test_id('reserve-1').click();page.get_by_test_id('units').fill('٢');page.get_by_test_id('submit').click()
                expect(page.get_by_role('dialog')).to_have_count(0);assert server.bootstrap()['parts'][0]['stock']==2
                text_is(page,page.get_by_test_id('stock-1'),message(page,'ar','parts.stock',count=2))
                visit(page,'activity');has_copy(page,'event.reserved','ar',actor='Robin',count=2,name='Adapter A')
        check('arabic_quantity_and_activity_state','robustness',reserve_digits)

        def fractional_rejection():
            with scene('fractions') as (page,server):
                language(page,'de');dialog(page,'charge');page.get_by_test_id('amount').fill('12,345');page.get_by_test_id('submit').click()
                text_is(page,page.get_by_test_id('dialog-error'),message(page,'de','error.AMOUNT_INVALID'));assert not server.bootstrap()['charges']
                page.get_by_test_id('amount').fill('0,01');page.get_by_test_id('submit').click();expect(page.get_by_role('dialog')).to_have_count(0)
                assert server.bootstrap()['charges'][0]['amount_minor']==1
        check('fractional_precision_and_small_charge','robustness',fractional_rejection)
        BROWSER.close()


if __name__=='__main__':
    try:main()
    except Exception as error:
        CHECKS['infrastructure']={'passed':False,'error':str(error),'traceback':traceback.format_exc()};print(traceback.format_exc(),flush=True)
    try:
        completion=json.loads((APP/'output/completion.json').read_text())
    except (OSError,ValueError) as error:
        completion={'_error':str(error)}
    rewards,verdict=grade(CHECKS,completion)
    (LOG/'checks.json').write_text(json.dumps(CHECKS,indent=2,ensure_ascii=False)+'\n')
    (LOG/'coverage.json').write_text(json.dumps({'required':len(EXPECTED),'executed':len(set(EXPECTED)&set(CHECKS)),'passed':sum(CHECKS.get(name,{}).get('passed') is True for name in EXPECTED),'cases':EXPECTED,'screenshot_warnings':SCREENSHOT_WARNINGS},indent=2)+'\n')
    (LOG/'reward.json').write_text(json.dumps(rewards,indent=2)+'\n')
    (LOG/'critical-outcomes.json').write_text(json.dumps(verdict,indent=2)+'\n')
    print(f'{sum(value.get("passed") is True for value in CHECKS.values())}/{len(EXPECTED)} checks passed',flush=True)
