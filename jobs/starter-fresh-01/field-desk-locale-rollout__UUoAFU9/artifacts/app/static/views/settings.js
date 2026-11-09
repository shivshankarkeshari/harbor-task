import {state} from '../core/state.js';
import {t} from '../core/locale.js';
export function render() {
  return `<h2 data-testid="page-title">Operator preferences</h2><p>Preferences belong to the selected operator.</p><section class="card"><label><span>Show operational notifications</span><input type="checkbox" data-testid="notifications" id="notifications" ${state.data.preferences.notifications?'checked':''}></label><p>Changing language must preserve this setting.</p><button data-action="save-settings" data-testid="save-settings">Save preferences</button></section><small data-testid="settings-operator">${t('settings.operatorNote',{name:state.operator==='robin'?'Robin':'Amal'})}</small>`;
}
