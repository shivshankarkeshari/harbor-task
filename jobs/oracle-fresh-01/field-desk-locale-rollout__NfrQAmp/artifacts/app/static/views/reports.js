import {state} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">${t('reports.title')}</h2><p>${t('reports.subtitle')}</p><div class="grid"><section class="card"><h3>${t('reports.open')}</h3><p data-testid="open-count">${t('reports.count',{count:state.data.orders.filter(row=>row.status!=='DONE').length})}</p></section><section class="card"><h3>${t('reports.budget')}</h3><p class="money">${money(state.data.orders.reduce((n,row)=>n+row.budget_minor,0))}</p></section></div>
    <button data-action="export" data-testid="export">${t('reports.export')}</button><p data-testid="export-note">${t('reports.exportNote')}</p>`;
}
export function dialog() {return modal(t('reports.dialogTitle'),`<p>${t('reports.dialogBody')}</p>`,'download');}
