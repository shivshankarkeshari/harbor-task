import {state} from '../core/state.js';
import {te} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${te('reports.title')}</h2><p>${te('reports.subtitle')}</p><div class="grid"><section class="card"><h3>${te('reports.open')}</h3><p data-testid="open-count">${te('reports.count',{count:state.data.orders.filter(row=>row.status!=='DONE').length})}</p></section><section class="card"><h3>${te('reports.budget')}</h3><p class="money">${money(state.data.orders.reduce((n,row)=>n+row.budget_minor,0))}</p></section></div>
    <button data-action="export" data-testid="export">${te('reports.export')}</button><p data-testid="export-note">${te('reports.exportNote')}</p>`;
}
export function dialog() {return modal(te('reports.dialogTitle'),`<p>${te('reports.dialogBody')}</p>`,'download');}
