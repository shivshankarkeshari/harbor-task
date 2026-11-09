import {state, escape} from '../core/state.js';
import {t} from '../core/locale.js';
import {modal, orderOptions} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">Crew dispatch</h2><p>Assign an available crew to an existing work order.</p><div class="grid">${state.data.crews.map(crew=>`<article class="card"><h3 class="user-content">${escape(crew.name)}</h3><p data-testid="crew-${crew.id}-status">${crew.available?"Available":"Unavailable"}</p><button data-action="assign" data-id="${crew.id}" data-testid="assign-${crew.id}">Assign crew <span class="link-arrow">→</span></button></article>`).join('')}</div>`;
}
export function dialog() {
  const crew = state.data.crews.find(row=>row.id===state.form.crew_id);
  return modal("Assign work order",`<p>${t('dispatch.assignTo',{name:crew.name})}</p><label>Work order<select id="order-id" data-field="order_id" data-testid="order-id">${orderOptions()}</select></label>`,'save-assignment');
}
