import {state, escape, value} from '../core/state.js';
import {t} from '../core/locale.js';
import {modal} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${t('parts.title')}</h2><p>${t('parts.subtitle')}</p><div class="grid">${state.data.parts.map(part=>`<article class="card"><h3 class="user-content">${escape(part.name)}</h3><p data-testid="stock-${part.id}">${t('parts.stock',{count:part.stock})}</p><button data-action="reserve" data-id="${part.id}" data-testid="reserve-${part.id}">${t('parts.reserve')}</button></article>`).join('')}</div>`;
}
export function dialog() {
  const part = state.data.parts.find(row=>row.id===state.form.part_id);
  return modal(t('parts.dialogTitle'),`<p class="user-content">${escape(part.name)}</p><label>${t('parts.quantity')}<input id="units" data-field="units" data-testid="units" value="${value('units')}" inputmode="numeric"></label><small>${t('parts.hint')}</small>`,'save-reservation');
}
