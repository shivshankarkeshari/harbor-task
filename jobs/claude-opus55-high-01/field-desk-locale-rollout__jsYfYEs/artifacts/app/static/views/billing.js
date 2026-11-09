import {state, escape, value} from '../core/state.js';
import {te} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${te('billing.title')}</h2><p>${te('billing.subtitle')}</p><button data-action="charge" data-testid="charge">${te('billing.record')}</button>
    <section class="card"><h3>${te('billing.total')}</h3><strong data-testid="charge-total" class="money">${money(state.data.charges.reduce((total,row)=>total+row.amount_minor,0))}</strong></section>
    ${state.data.charges.length?`<table><thead><tr><th>${te('field.order')}</th><th>${te('billing.amount')}</th><th>${te('billing.memo')}</th></tr></thead><tbody>${state.data.charges.map(row=>`<tr><td>#${row.order_id}</td><td class="money">${money(row.amount_minor)}</td><td class="user-content" dir="auto">${escape(row.memo)}</td></tr>`).join('')}</tbody></table>`:`<p data-testid="charges-empty">${te('billing.empty')}</p>`}`;
}
export function dialog() {
  return modal(te('billing.dialogTitle'),`<label>${te('field.order')}<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>
    <label>${te('billing.amount')}<input id="amount" data-field="amount" data-testid="amount" value="${value('amount')}" inputmode="decimal"></label>
    <label>${te('billing.memo')}<textarea id="memo" data-field="memo" data-testid="memo" dir="auto" placeholder="${te('billing.memoHint')}">${value('memo')}</textarea></label>`,'save-charge');
}
