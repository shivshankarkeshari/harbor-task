import {state, api, reload} from './core/state.js';
import {loadCatalogs, t, setLanguage, applyDirection} from './core/locale.js';
import {parseAmount, inputAmount, localizeDraft} from './core/format.js';
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
let rendering=false;
function render() {
  rendering=true;
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
  rendering=false;
}
function open(kind, form={}) {state.modal=kind;state.form=form;state.error=null;render();}
function close() {state.modal=null;state.form={};state.error=null;render();}
function notice(key,args={}) {state.notice={key,args};}
function whole(raw) {
  const text=String(raw).trim().replace(/[٠-٩]/g,ch=>String(ch.charCodeAt(0)-0x660));
  return /^\d+$/.test(text)?Number(text):null;
}
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
      const amount=parseAmount(state.form.budget,state.form.amountLocale);
      if (amount===null) throw {code:'AMOUNT_INVALID'};
      await api('order',{id:state.form.id,title:state.form.title,customer:state.form.customer,budget_minor:amount});
      notice('notice.saved',{title:state.form.title});
    } else if (name==='save-assignment') {
      await api('assign',{order_id:Number(state.form.order_id),crew_id:state.form.crew_id});notice('notice.assigned');
    } else if (name==='save-reservation') {
      await api('reserve',{part_id:state.form.part_id,units:whole(state.form.units)});notice('notice.reserved');
    } else if (name==='save-charge') {
      const amount=parseAmount(state.form.amount,state.form.amountLocale);
      if (amount===null) throw {code:'AMOUNT_INVALID'};
      await api('charge',{order_id:Number(state.form.order_id),amount_minor:amount,memo:state.form.memo});notice('notice.charged');
    } else if (name==='complete') {
      await api('complete',{ids:state.selected});notice('notice.completed',{count:state.selected.length});state.selected=[];
    } else if (name==='save-settings') {
      const notifications=document.getElementById('notifications').checked;
      await api('preferences',{locale:state.locale,notifications});notice('notice.preferences');
    } else if (name==='download') {
      const response=await fetch('/api/export');
      const url=URL.createObjectURL(await response.blob());
      const link=document.createElement('a');link.href=url;link.download='work-orders.csv';link.click();URL.revokeObjectURL(url);
      notice('notice.exported');
    } else if (name==='copy-help') {
      const text=t('help.copyText');
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
      notice('common.copied');render();
      document.querySelector('[data-testid="help-copy-result"]').textContent=t('common.copied');return;
    } else return;
    await reload();close();
  } catch (error) {state.error=error;render();}
}

document.addEventListener('click',event=>{
  const button=event.target.closest('[data-action]');
  if (button && !button.disabled) action(button.dataset.action,Number(button.dataset.id));
});
document.addEventListener('input',event=>{
  const element=event.target;
  if(rendering || !element.isConnected)return;
  if (element.dataset.field) {
    state.form[element.dataset.field]=element.value;
    if (['budget','amount'].includes(element.dataset.field)) state.form.amountLocale=state.locale;
  }
  if (element.dataset.viewField) {state[element.dataset.viewField]=element.value;render();}
});
document.addEventListener('change',async event=>{
  const element=event.target;
  if(rendering || !element.isConnected)return;
  if (element.id==='language') {
    const previous=state.locale;
    await setLanguage(element.value);localizeDraft(previous);render();
  } else if (element.id==='operator') {
    state.operator=element.value;localStorage.setItem('field-desk.operator',state.operator);
    state.modal=null;state.notice=null;state.error=null;state.selected=[];
    await reload();state.locale=state.data.preferences.locale;applyDirection();render();
  } else if (element.dataset.select) {
    const id=Number(element.dataset.select);
    state.selected=element.checked?[...new Set([...state.selected,id])]:state.selected.filter(value=>value!==id);render();
  } else if (element.dataset.field) state.form[element.dataset.field]=element.value;
  else if (element.dataset.viewField) {state[element.dataset.viewField]=element.value;render();}
});
window.addEventListener('hashchange',()=>{state.route=location.hash.slice(1)||'orders';state.modal=null;state.error=null;render();});
await loadCatalogs();await reload();state.locale=state.data.preferences.locale;applyDirection();render();
