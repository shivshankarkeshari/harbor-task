import {state} from '../core/state.js';
import {t} from '../core/locale.js';
import {money} from '../core/format.js';
import {modal} from '../core/shell.js';
export function render() {
  return `<h2 data-testid="page-title">Operational reports</h2><p>Review progress and export stable machine-readable data.</p><div class="grid"><section class="card"><h3>Active work</h3><p data-testid="open-count">${t('reports.count',{count:state.data.orders.filter(row=>row.status!=='DONE').length})}</p></section><section class="card"><h3>Total planned budget</h3><p class="money">${money(state.data.orders.reduce((n,row)=>n+row.budget_minor,0))}</p></section></div>
    <button data-action="export" data-testid="export">Export CSV</button><p data-testid="export-note">CSV headers, status codes, user text, and cent amounts stay unchanged.</p>`;
}
export function dialog() {return modal("Export work orders",`<p>Download all work orders using the documented CSV contract.</p>`,'download');}
