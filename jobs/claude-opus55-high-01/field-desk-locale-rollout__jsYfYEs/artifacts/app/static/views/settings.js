import {state} from '../core/state.js';
import {te} from '../core/locale.js';
export function render() {
  const enabled = state.notificationsDraft ?? Boolean(state.data.preferences.notifications);
  return `<h2 data-testid="page-title">${te('settings.title')}</h2><p>${te('settings.subtitle')}</p><section class="card"><label><span>${te('settings.notifications')}</span><input type="checkbox" data-testid="notifications" id="notifications" ${enabled?'checked':''}></label><p>${te('settings.notificationsHint')}</p><button data-action="save-settings" data-testid="save-settings">${te('common.save')}</button></section><small data-testid="settings-operator">${te('settings.operatorNote',{name:state.data.operators.find(user=>user.id===state.operator)?.name??state.operator})}</small>`;
}
