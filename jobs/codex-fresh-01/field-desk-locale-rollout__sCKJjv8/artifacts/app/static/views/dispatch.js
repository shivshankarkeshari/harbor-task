import {state, escape} from '../core/state.js';
import {t} from '../core/locale.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${t('dispatch.title')}</h2><p>${t('dispatch.subtitle')}</p><div class="grid">${state.data.crews.map(crew=>`<article class="card"><h3 class="user-content">${escape(crew.name)}</h3><p data-testid="crew-${crew.id}-status">${t(crew.available?'dispatch.available':'dispatch.unavailable')}</p><button data-action="assign" data-id="${crew.id}" data-testid="assign-${crew.id}">${t('dispatch.assign')} <span class="link-arrow">→</span></button></article>`).join('')}</div>`;
}
export function dialog() {
  const crew = state.data.crews.find(row=>row.id===state.form.crew_id);
  return modal(t('dispatch.dialogTitle'),`<p>${escape(t('dispatch.assignTo',{name:crew.name}))}</p><label>${t('field.order')}<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>`,'save-assignment');
}
