import {state, escape, value} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${t('billing.title')}</h2><p>${t('billing.subtitle')}</p><button data-action="charge" data-testid="charge">${t('billing.record')}</button>
    <section class="card"><h3>${t('billing.total')}</h3><strong data-testid="charge-total" class="money">${money(state.data.charges.reduce((total,row)=>total+row.amount_minor,0))}</strong></section>
    ${state.data.charges.length?`<table><thead><tr><th>${t('field.order')}</th><th>${t('billing.amount')}</th><th>${t('billing.memo')}</th></tr></thead><tbody>${state.data.charges.map(row=>`<tr><td>#${row.order_id}</td><td>${money(row.amount_minor)}</td><td class="user-content">${escape(row.memo)}</td></tr>`).join('')}</tbody></table>`:`<p data-testid="charges-empty">${t('billing.empty')}</p>`}`;
}
export function dialog() {
  return modal(t('billing.dialogTitle'),`<label>${t('field.order')}<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>
    <label>${t('billing.amount')}<input id="amount" data-field="amount" data-testid="amount" value="${value('amount')}" inputmode="decimal"></label>
    <label>${t('billing.memo')}<textarea id="memo" data-field="memo" data-testid="memo" placeholder="${t('billing.memoHint')}">${value('memo')}</textarea></label>`,'save-charge');
}
