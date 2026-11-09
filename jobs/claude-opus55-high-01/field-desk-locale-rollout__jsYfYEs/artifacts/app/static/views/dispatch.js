import {state, escape} from '../core/state.js';
import {te} from '../core/locale.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${te('dispatch.title')}</h2><p>${te('dispatch.subtitle')}</p><div class="grid">${state.data.crews.map(crew=>`<article class="card"><h3 class="user-content" dir="auto">${escape(crew.name)}</h3><p data-testid="crew-${crew.id}-status">${crew.available?te('dispatch.available'):te('dispatch.unavailable')}</p><button data-action="assign" data-id="${crew.id}" data-testid="assign-${crew.id}">${te('dispatch.assign')} <span class="link-arrow" aria-hidden="true">→</span></button></article>`).join('')}</div>`;
}
export function dialog() {
  const crew = state.data.crews.find(row=>row.id===state.form.crew_id);
  return modal(te('dispatch.dialogTitle'),`<p>${te('dispatch.assignTo',{name:crew?.name??''})}</p><label>${te('field.order')}<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>`,'save-assignment');
}
