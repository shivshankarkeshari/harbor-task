import {state, escape, value} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, status} from '../core/shell.js';
export function render() {
  const rows = state.data.orders.filter(order=>(state.filter==='ALL'||order.status===state.filter)
    && `${order.title} ${order.customer}`.toLowerCase().includes(state.search.toLowerCase()));
  return `<h2 data-testid="page-title">Work orders</h2><p data-testid="orders-subtitle">Plan work, assign crews, and preserve the job details.</p>
    <div class="toolbar"><label>Search orders<input id="search" data-testid="search" data-view-field="search" value="${escape(state.search)}" placeholder="Search title or customer"></label>
    <label>Status filter<select id="filter" data-testid="filter" data-view-field="filter">${[['ALL',"All statuses"],['OPEN',status('OPEN')],['ASSIGNED',status('ASSIGNED')],['DONE',status('DONE')]].map(([v,l])=>`<option value="${v}" ${state.filter===v?'selected':''}>${l}</option>`).join('')}</select></label>
    <button data-action="new-order" data-testid="new-order">New work order</button><button data-action="bulk" data-testid="bulk">Complete selected</button></div>
    <p data-testid="selection-count">${t('orders.selected',{count:state.selected.length})}</p>
    ${rows.length?`<table><thead><tr><th>Select</th><th>Title</th><th>Customer</th><th>Status</th><th>Budget (EUR)</th><th>Actions</th></tr></thead><tbody>${rows.map(order=>`<tr data-testid="order-${order.id}"><td><input type="checkbox" data-select="${order.id}" data-testid="select-${order.id}" ${state.selected.includes(order.id)?'checked':''} aria-label="${escape(t('orders.selectOne',{title:order.title}))}"></td><td class="user-content">${escape(order.title)}</td><td class="user-content">${escape(order.customer)}</td><td data-testid="status-${order.id}" class="badge">${status(order.status)}</td><td class="money">${money(order.budget_minor)}</td><td><button data-action="edit-order" data-id="${order.id}" data-testid="edit-${order.id}">Edit</button></td></tr>`).join('')}</tbody></table>`:`<section class="card" data-testid="empty"><h3>No matching work orders</h3><p>Try a different search or clear the filters.</p><button data-action="clear-search" data-testid="clear-search">Clear search</button></section>`}`;
}
export function orderDialog() {
  return modal(state.form.id?"Edit work order":"Create work order",
    `<label>Title<input id="title" data-field="title" data-testid="title" value="${value('title')}" placeholder="Describe the work"></label>
    <label>Customer<input id="customer" data-field="customer" data-testid="customer" value="${value('customer')}"></label>
    <label>Budget (EUR)<input id="budget" data-field="budget" data-testid="budget" value="${value('budget')}" inputmode="decimal"></label><small data-testid="amount-hint">Use your language's decimal separator; at most two decimal places.</small>`, 'save-order');
}
export function bulkDialog() {
  return modal("Complete work orders",`<p data-testid="bulk-question">${t('bulk.question',{count:state.selected.length})}</p><p>Customer titles and stored codes will not be changed.</p>`,'complete');
}
