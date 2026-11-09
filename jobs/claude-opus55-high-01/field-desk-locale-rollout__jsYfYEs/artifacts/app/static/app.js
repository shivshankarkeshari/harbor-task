import {state, api, reload} from './core/state.js';
import {loadCatalogs, t, setLanguage, supported} from './core/locale.js';
import {parseAmount, inputAmount, parseWhole} from './core/format.js';
import {header, navigation} from './core/shell.js';
import * as orders from './views/orders.js';
import * as dispatch from './views/dispatch.js';
import * as parts from './views/parts.js';
import * as billing from './views/billing.js';
import * as activity from './views/activity.js';
import * as reports from './views/reports.js';
import * as settings from './views/settings.js';
import * as help from './views/help.js';

const views = {orders,dispatch,parts,billing,activity,reports,settings,help};
const AMOUNT_FIELDS = ['budget','amount'];
function render() {
  const active = document.activeElement;
  const focus = active?.id;
  const selection = typeof active?.selectionStart === 'number' ? [active.selectionStart,active.selectionEnd] : null;
  document.getElementById('header').innerHTML = header();
  document.getElementById('navigation').innerHTML = navigation();
  document.getElementById('main').innerHTML = (views[state.route] || orders).render();
  const modal = state.modal === 'order' ? orders.orderDialog() : state.modal === 'bulk' ? orders.bulkDialog()
    : state.modal === 'assign' ? dispatch.dialog() : state.modal === 'reserve' ? parts.dialog()
    : state.modal === 'charge' ? billing.dialog() : state.modal === 'export' ? reports.dialog() : '';
  document.getElementById('modal-root').innerHTML = modal;
  document.getElementById('toast').textContent = state.notice ? t(state.notice.key, state.notice.args) : '';
  if (focus) {
    const next = document.getElementById(focus);
    next?.focus();
    if (selection && next?.setSelectionRange) try {next.setSelectionRange(...selection);} catch {}
  }
}
function open(kind, form={}) {state.modal=kind;state.form=form;state.error=null;render();}
function close() {state.modal=null;state.form={};state.error=null;render();}
function notice(key,args={}) {state.notice={key,args};}
function amountOf(field) {
  const amount=parseAmount(state.form[field],state.form.amountLocale||state.locale);
  if (amount===null) throw {code:'AMOUNT_INVALID'};
  return amount;
}
/** The operator's saved locale, falling back to English for unknown values. */
const savedLocale = () => supported(state.data?.preferences?.locale) ? state.data.preferences.locale : 'en';

async function action(name, id) {
  state.error=null;
  try {
    if (name==='new-order') return open('order',{title:'',customer:'',budget:inputAmount(0),amountLocale:state.locale});
    if (name==='edit-order') {
      const row=state.data.orders.find(row=>row.id===id);
      return open('order',{...row,budget:inputAmount(row.budget_minor),amountLocale:state.locale});
    }
    if (name==='close') return close();
    if (name==='clear-search') {state.search='';state.filter='ALL';return render();}
    if (name==='bulk') return open('bulk');
    if (name==='assign') return open('assign',{crew_id:id,order_id:state.data.orders[0].id});
    if (name==='reserve') return open('reserve',{part_id:id,units:'1'});
    if (name==='charge') return open('charge',{order_id:state.data.orders[0].id,amount:inputAmount(0),amountLocale:state.locale,memo:''});
    if (name==='export') return open('export');
    if (name==='save-order') {
      const amount=amountOf('budget');
      await api('order',{id:state.form.id,title:state.form.title,customer:state.form.customer,budget_minor:amount});
      notice('notice.saved',{title:state.form.title});
    } else if (name==='save-assignment') {
      await api('assign',{order_id:Number(state.form.order_id),crew_id:state.form.crew_id});notice('notice.assigned');
    } else if (name==='save-reservation') {
      await api('reserve',{part_id:state.form.part_id,units:parseWhole(state.form.units)});notice('notice.reserved');
    } else if (name==='save-charge') {
      const amount=amountOf('amount');
      await api('charge',{order_id:Number(state.form.order_id),amount_minor:amount,memo:state.form.memo});notice('notice.charged');
    } else if (name==='complete') {
      await api('complete',{ids:state.selected});notice('notice.completed',{count:state.selected.length});state.selected=[];
    } else if (name==='save-settings') {
      const notifications=document.getElementById('notifications').checked;
      await api('preferences',{locale:state.locale,notifications});
      state.data.preferences={...state.data.preferences,locale:state.locale,notifications:notifications?1:0};
      state.notificationsDraft=null;notice('notice.preferences');
    } else if (name==='download') {
      const response=await fetch('/api/export');
      const url=URL.createObjectURL(await response.blob());
      const link=document.createElement('a');link.href=url;link.download='work-orders.csv';link.click();URL.revokeObjectURL(url);
      notice('notice.exported');
    } else if (name==='copy-help') {
      const text=t('help.copyText');
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
      notice('common.copied');state.helpCopied=true;return render();
    } else return;
    await reload();close();
  } catch (error) {state.error=error;render();}
}

/** Re-express open amount drafts in the new locale so their numeric meaning is unchanged. */
function convertDrafts(locale) {
  for (const field of AMOUNT_FIELDS) {
    if (!(field in state.form)) continue;
    const minor=parseAmount(state.form[field],state.form.amountLocale||state.locale);
    // Unparseable drafts keep their text and original locale, so they are still read with their original meaning.
    if (minor!==null) {state.form[field]=inputAmount(minor,locale);state.form.amountLocale=locale;}
  }
}
async function changeLanguage(locale) {
  if (!supported(locale) || locale===state.locale) return;
  convertDrafts(locale);
  setLanguage(locale);render();
  const operator=state.operator;
  try {
    // Persist for this operator while keeping the saved (not draft) notification preference.
    await api('preferences',{locale,notifications:Boolean(state.data.preferences.notifications)});
    if (state.operator===operator) state.data.preferences={...state.data.preferences,locale};
  } catch (error) {notice('error.REQUEST_FAILED');render();}
}
async function switchOperator(operator) {
  state.operator=operator;localStorage.setItem('field-desk.operator',state.operator);
  state.modal=null;state.form={};state.notice=null;state.error=null;state.selected=[];
  state.notificationsDraft=null;state.helpCopied=false;
  await reload();setLanguage(savedLocale());render();
}

document.addEventListener('click',event=>{
  const button=event.target.closest('[data-action]');
  if (button && !button.disabled) action(button.dataset.action,Number(button.dataset.id));
});
document.addEventListener('input',event=>{
  const element=event.target;
  if (element.dataset.field) {
    state.form[element.dataset.field]=element.value;
    if (AMOUNT_FIELDS.includes(element.dataset.field)) state.form.amountLocale=state.locale;
  }
  if (element.dataset.viewField) {state[element.dataset.viewField]=element.value;render();}
});
document.addEventListener('change',async event=>{
  const element=event.target;
  if (element.id==='language') await changeLanguage(element.value);
  else if (element.id==='operator') await switchOperator(element.value);
  else if (element.id==='notifications') state.notificationsDraft=element.checked;
  else if (element.dataset.select) {
    const id=Number(element.dataset.select);
    state.selected=element.checked?[...new Set([...state.selected,id])]:state.selected.filter(value=>value!==id);render();
  } else if (element.dataset.field && element.tagName==='SELECT') state.form[element.dataset.field]=element.value;
  // Text fields are captured by `input` events; a late `change` could restore pre-conversion amount text.
  else if (element.dataset.viewField) {state[element.dataset.viewField]=element.value;render();}
});
window.addEventListener('hashchange',()=>{state.route=location.hash.slice(1)||'orders';state.modal=null;state.error=null;state.helpCopied=false;render();});
await loadCatalogs();
try {await reload();} catch {
  // A stale stored operator id falls back to the default operator.
  state.operator='robin';localStorage.setItem('field-desk.operator',state.operator);await reload();
}
setLanguage(savedLocale());render();
