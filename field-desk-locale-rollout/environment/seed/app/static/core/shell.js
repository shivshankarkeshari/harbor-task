import {state, escape} from './state.js';
import {t, errorText} from './locale.js';
export function header() {
  return `<h1>Field Desk</h1><label>Operator<select id="operator" data-testid="operator">${state.data.operators.map(user=>`<option value="${user.id}" ${state.operator===user.id?'selected':''}>${escape(user.name)}</option>`).join('')}</select></label>
    <label>Language<select id="language" data-testid="language">${[['en','English'],['de','Deutsch'],['ar','العربية']].map(([code,name])=>`<option value="${code}" ${state.locale===code?'selected':''}>${name}</option>`).join('')}</select></label>`;
}
export function navigation() {
  const links = [
    ['orders', "Work orders"], ['dispatch', "Dispatch"], ['parts', "Parts"],
    ['billing', "Billing"], ['activity', "Activity"], ['reports', "Reports"],
    ['settings', "Settings"], ['help', "Help"],
  ];
  return links.map(([route,label])=>`<a data-testid="nav-${route}" href="#${route}" class="${state.route===route?'active':''}">${label}</a>`).join('');
}
export function status(code) {return t(`status.${code}`);}
export function modal(title, body, action) {
  return `<div class="modal-overlay"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="dialog-title"><button class="close" data-action="close" data-testid="dialog-x" aria-label="Close">×</button><h2 id="dialog-title" data-testid="dialog-title">${title}</h2>${body}<div role="alert" data-testid="dialog-error" class="error">${state.error?escape(errorText(state.error)):''}</div><div class="modal-actions"><button data-action="close" data-testid="cancel">Cancel</button><button class="primary" data-action="${action}" data-testid="submit">Confirm</button></div></section></div>`;
}
export function orderOptions() {return state.data.orders.map(order=>`<option value="${order.id}" ${String(state.form.order_id)===String(order.id)?'selected':''}>#${order.id} ${escape(order.title)}</option>`).join('');}
