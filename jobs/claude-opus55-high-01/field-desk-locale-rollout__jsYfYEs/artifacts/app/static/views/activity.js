import {state} from '../core/state.js';
import {te} from '../core/locale.js';
const actorName = actor => actor==='robin'?'Robin':actor==='amal'?'Amal':actor;
function payload(raw) {try {return JSON.parse(raw) || {};} catch {return {};}}
export function render() {
  return `<h2 data-testid="page-title">${te('activity.title')}</h2><p>${te('activity.subtitle')}</p><section class="card"><ul>${state.data.activity.map(event=>`<li data-testid="event-${event.id}">${te(`event.${event.kind}`,{...payload(event.payload),actor:actorName(event.actor)})}</li>`).join('')}</ul></section>`;
}
