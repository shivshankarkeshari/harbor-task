import {state, escape} from '../core/state.js';
import {t} from '../core/locale.js';
export function render() {
  return `<h2 data-testid="page-title">Activity log</h2><p>Events describe actions; customer wording stays unchanged.</p><section class="card"><ul>${state.data.activity.map(event=>`<li data-testid="event-${event.id}">${escape(t(`event.${event.kind}`,{...JSON.parse(event.payload),actor:event.actor==='robin'?'Robin':'Amal'}))}</li>`).join('')}</ul></section>`;
}
