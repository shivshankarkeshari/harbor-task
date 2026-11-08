import {state, escape, value} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">Work-order billing</h2><p>Record charges in euros; stored amounts use integer cents.</p><button data-action="charge" data-testid="charge">Record charge</button>
    <section class="card"><h3>Total recorded charges</h3><strong data-testid="charge-total" class="money">${money(state.data.charges.reduce((total,row)=>total+row.amount_minor,0))}</strong></section>
    ${state.data.charges.length?`<table><thead><tr><th>Work order</th><th>Amount (EUR)</th><th>Internal memo</th></tr></thead><tbody>${state.data.charges.map(row=>`<tr><td>#${row.order_id}</td><td>${money(row.amount_minor)}</td><td class="user-content">${escape(row.memo)}</td></tr>`).join('')}</tbody></table>`:`<p data-testid="charges-empty">No charges recorded</p>`}`;
}
export function dialog() {
  return modal("Record a charge",`<label>Work order<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>
    <label>Amount (EUR)<input id="amount" data-field="amount" data-testid="amount" value="${value('amount')}" inputmode="decimal"></label>
    <label>Internal memo<textarea id="memo" data-field="memo" data-testid="memo" placeholder="Keep the customer's wording">${value('memo')}</textarea></label>`,'save-charge');
}
