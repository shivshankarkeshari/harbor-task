import {state, escape, value} from '../core/state.js';
import {te} from '../core/locale.js';
import {modal} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${te('parts.title')}</h2><p>${te('parts.subtitle')}</p><div class="grid">${state.data.parts.map(part=>`<article class="card"><h3 class="user-content" dir="auto">${escape(part.name)}</h3><p data-testid="stock-${part.id}">${te('parts.stock',{count:part.stock})}</p><button data-action="reserve" data-id="${part.id}" data-testid="reserve-${part.id}">${te('parts.reserve')}</button></article>`).join('')}</div>`;
}
export function dialog() {
  const part = state.data.parts.find(row=>row.id===state.form.part_id);
  return modal(te('parts.dialogTitle'),`<p class="user-content" dir="auto">${escape(part?.name)}</p><label>${te('parts.quantity')}<input id="units" data-field="units" data-testid="units" value="${value('units')}" inputmode="numeric"></label><small>${te('parts.hint')}</small>`,'save-reservation');
}
