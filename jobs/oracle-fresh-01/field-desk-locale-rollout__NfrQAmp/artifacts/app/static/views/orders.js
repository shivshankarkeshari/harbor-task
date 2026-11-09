import {state, escape, value} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, status} from '../core/shell.js';
export function render() {
  const rows = state.data.orders.filter(order=>(state.filter==='ALL'||order.status===state.filter)
    && `${order.title} ${order.customer}`.toLowerCase().includes(state.search.toLowerCase()));
  return `<h2 data-testid="page-title">${t('orders.title')}</h2><p data-testid="orders-subtitle">${t('orders.subtitle')}</p>
    <div class="toolbar"><label>${t('orders.search')}<input id="search" data-testid="search" data-view-field="search" value="${escape(state.search)}" placeholder="${t('orders.searchHint')}"></label>
    <label>${t('orders.filter')}<select id="filter" data-testid="filter" data-view-field="filter">${[['ALL',t('orders.all')],['OPEN',status('OPEN')],['ASSIGNED',status('ASSIGNED')],['DONE',status('DONE')]].map(([v,l])=>`<option value="${v}" ${state.filter===v?'selected':''}>${l}</option>`).join('')}</select></label>
    <button data-action="new-order" data-testid="new-order">${t('orders.new')}</button><button data-action="bulk" data-testid="bulk">${t('orders.complete')}</button></div>
    <p data-testid="selection-count">${t('orders.selected',{count:state.selected.length})}</p>
    ${rows.length?`<table><thead><tr><th>${t('orders.choose')}</th><th>${t('field.title')}</th><th>${t('field.customer')}</th><th>${t('field.status')}</th><th>${t('field.budget')}</th><th>${t('field.actions')}</th></tr></thead><tbody>${rows.map(order=>`<tr data-testid="order-${order.id}"><td><input type="checkbox" data-select="${order.id}" data-testid="select-${order.id}" ${state.selected.includes(order.id)?'checked':''} aria-label="${escape(t('orders.selectOne',{title:order.title}))}"></td><td class="user-content">${escape(order.title)}</td><td class="user-content">${escape(order.customer)}</td><td data-testid="status-${order.id}" class="badge">${status(order.status)}</td><td class="money">${money(order.budget_minor)}</td><td><button data-action="edit-order" data-id="${order.id}" data-testid="edit-${order.id}">${t('orders.edit')}</button></td></tr>`).join('')}</tbody></table>`:`<section class="card" data-testid="empty"><h3>${t('orders.emptyTitle')}</h3><p>${t('orders.emptyBody')}</p><button data-action="clear-search" data-testid="clear-search">${t('common.clear')}</button></section>`}`;
}
export function orderDialog() {
  return modal(state.form.id?t('order.editTitle'):t('order.createTitle'),
    `<label>${t('field.title')}<input id="title" data-field="title" data-testid="title" value="${value('title')}" placeholder="${t('order.titleHint')}"></label>
    <label>${t('field.customer')}<input id="customer" data-field="customer" data-testid="customer" value="${value('customer')}"></label>
    <label>${t('field.budget')}<input id="budget" data-field="budget" data-testid="budget" value="${value('budget')}" inputmode="decimal"></label><small data-testid="amount-hint">${t('order.amountHint')}</small>`, 'save-order');
}
export function bulkDialog() {
  return modal(t('bulk.title'),`<p data-testid="bulk-question">${t('bulk.question',{count:state.selected.length})}</p><p>${t('bulk.warning')}</p>`,'complete');
}
