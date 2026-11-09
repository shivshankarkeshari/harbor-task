import {state, escape, value} from '../core/state.js';
import {te} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, status} from '../core/shell.js';
export function render() {
  const rows = state.data.orders.filter(order=>(state.filter==='ALL'||order.status===state.filter)
    && `${order.title} ${order.customer}`.toLowerCase().includes(state.search.toLowerCase()));
  return `<h2 data-testid="page-title">${te('orders.title')}</h2><p data-testid="orders-subtitle">${te('orders.subtitle')}</p>
    <div class="toolbar"><label>${te('orders.search')}<input id="search" data-testid="search" data-view-field="search" dir="auto" value="${escape(state.search)}" placeholder="${te('orders.searchHint')}"></label>
    <label>${te('orders.filter')}<select id="filter" data-testid="filter" data-view-field="filter">${[['ALL',te('orders.all')],['OPEN',status('OPEN')],['ASSIGNED',status('ASSIGNED')],['DONE',status('DONE')]].map(([v,l])=>`<option value="${v}" ${state.filter===v?'selected':''}>${l}</option>`).join('')}</select></label>
    <button data-action="new-order" data-testid="new-order">${te('orders.new')}</button><button data-action="bulk" data-testid="bulk">${te('orders.complete')}</button></div>
    <p data-testid="selection-count">${te('orders.selected',{count:state.selected.length})}</p>
    ${rows.length?`<table><thead><tr><th>${te('orders.choose')}</th><th>${te('field.title')}</th><th>${te('field.customer')}</th><th>${te('field.status')}</th><th>${te('field.budget')}</th><th>${te('field.actions')}</th></tr></thead><tbody>${rows.map(order=>`<tr data-testid="order-${order.id}"><td><input type="checkbox" data-select="${order.id}" data-testid="select-${order.id}" ${state.selected.includes(order.id)?'checked':''} aria-label="${te('orders.selectOne',{title:order.title})}"></td><td class="user-content" dir="auto">${escape(order.title)}</td><td class="user-content" dir="auto">${escape(order.customer)}</td><td data-testid="status-${order.id}" class="badge">${status(order.status)}</td><td class="money">${money(order.budget_minor)}</td><td><button data-action="edit-order" data-id="${order.id}" data-testid="edit-${order.id}">${te('orders.edit')}</button></td></tr>`).join('')}</tbody></table>`:`<section class="card" data-testid="empty"><h3>${te('orders.emptyTitle')}</h3><p>${te('orders.emptyBody')}</p><button data-action="clear-search" data-testid="clear-search">${te('common.clear')}</button></section>`}`;
}
export function orderDialog() {
  return modal(state.form.id?te('order.editTitle'):te('order.createTitle'),
    `<label>${te('field.title')}<input id="title" data-field="title" data-testid="title" dir="auto" value="${value('title')}" placeholder="${te('order.titleHint')}"></label>
    <label>${te('field.customer')}<input id="customer" data-field="customer" data-testid="customer" dir="auto" value="${value('customer')}"></label>
    <label>${te('field.budget')}<input id="budget" data-field="budget" data-testid="budget" value="${value('budget')}" inputmode="decimal"></label><small data-testid="amount-hint">${te('order.amountHint')}</small>`, 'save-order');
}
export function bulkDialog() {
  return modal(te('bulk.title'),`<p data-testid="bulk-question">${te('bulk.question',{count:state.selected.length})}</p><p>${te('bulk.warning')}</p>`,'complete');
}
