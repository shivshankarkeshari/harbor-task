"""Replay the frozen failure and a keyboard workflow with a delayed preferences response."""
import asyncio
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0, '/tests')
import verify
from playwright.async_api import async_playwright, expect

BASE=Path('/logs/verifier')
CASE='live_draft_numeric_meaning_and_view_state'
results=[]
original=verify.check

def only_case(name,category,function):
    if name!=CASE:return
    for attempt in range(1,4):
        verify.LOG=BASE/f'frozen-{attempt}'
        verify.LOG.mkdir(parents=True,exist_ok=True)
        original(name,category,function)
        results.append({'variant':'frozen_case','attempt':attempt,**copy.deepcopy(verify.CHECKS[name])})

if "--pending-edit-only" not in sys.argv:
    verify.check=only_case
    verify.main()

async def keyboard_flow(delay_response,attempt):
    variant='keyboard_pending_preferences_edit' if delay_response else 'keyboard_normal'
    folder=BASE/f'{variant}-{attempt}';folder.mkdir(parents=True,exist_ok=True)
    verify.LOG=folder
    server=verify.Server(variant)
    try:
        async with async_playwright() as p:
            browser=await p.chromium.launch(headless=True,args=['--no-sandbox'])
            page=await browser.new_page(viewport={'width':1280,'height':900})
            await page.goto(server.url)
            await expect(page.get_by_test_id('language')).to_be_visible()
            await page.get_by_test_id('language').focus()
            await page.get_by_test_id('language').press('Home')
            await page.get_by_test_id('language').press('ArrowDown')
            await expect(page.locator('html')).to_have_attribute('lang','de')
            await page.get_by_test_id('search').fill('Ready')
            await page.get_by_test_id('filter').select_option('OPEN')
            await page.get_by_test_id('select-1').check()
            await page.get_by_test_id('edit-1').click()
            await page.get_by_test_id('title').fill('Open House: keep this wording')
            await page.get_by_test_id('customer').fill('Ready for pickup')
            await page.get_by_test_id('budget').fill('1.234,50')
            request_seen=asyncio.Event();release=asyncio.Event()
            if delay_response:
                async def hold(route):
                    response=await route.fetch()
                    request_seen.set()
                    await release.wait()
                    await route.fulfill(response=response)
                await page.route('**/api/preferences',hold)
            await page.get_by_test_id('language').focus()
            await page.get_by_test_id('language').press('End')
            if delay_response:
                await asyncio.wait_for(request_seen.wait(),5)
                entry_locale=await page.locator('html').get_attribute('lang')
                entry={'de':'1.234,51','ar':'١٢٣٤٫٥١','en':'1,234.51'}[entry_locale]
                await page.get_by_test_id('budget').fill(entry)
                release.set()
            await expect(page.locator('html')).to_have_attribute('lang','ar')
            # Let all immediate events settle: this is not a fast-submit timeout.
            await page.wait_for_timeout(500)
            draft=await page.evaluate("async()=>{const {state}=await import('/core/state.js');return {form:structuredClone(state.form),locale:state.locale,focused:document.activeElement?.id};}")
            await page.get_by_test_id('submit').click()
            await page.wait_for_timeout(500)
            persisted=server.bootstrap()['orders'][0]
            passed=await page.get_by_role('dialog').count()==0 and persisted['budget_minor']==(123451 if delay_response else 123450) and persisted['title']=='Open House: keep this wording'
            outcome={'variant':variant,'attempt':attempt,'passed':passed,'draft_before_submit':draft,'persisted_after_submit':persisted,'dialog_count':await page.get_by_role('dialog').count()}
            await page.screenshot(path=str(folder/'after-submit.png'),full_page=True)
            (folder/'visible.txt').write_text(await page.locator('body').inner_text())
            (folder/'outcome.json').write_text(json.dumps(outcome,indent=2,ensure_ascii=False)+'\n')
            results.append(outcome)
            await browser.close()
    finally:server.stop()

for delayed in ([True] if "--pending-edit-only" in sys.argv else [False,True]):
    for attempt in range(1,4):asyncio.run(keyboard_flow(delayed,attempt))
(BASE/'reproduction.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
print(json.dumps([{'variant':v,'passed':sum(x['passed'] for x in results if x['variant']==v),'attempts':sum(x['variant']==v for x in results)} for v in ['frozen_case','keyboard_normal','keyboard_pending_preferences_edit']]))
