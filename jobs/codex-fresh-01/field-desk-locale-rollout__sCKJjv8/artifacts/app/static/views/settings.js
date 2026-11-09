import {state} from '../core/state.js';
import {t} from '../core/locale.js';
export function render() {
  return `<h2 data-testid="page-title">${t('settings.title')}</h2><p>${t('settings.subtitle')}</p><section class="card"><label><span>${t('settings.notifications')}</span><input type="checkbox" data-testid="notifications" id="notifications" ${(state.notificationDraft ?? state.data.preferences.notifications)?'checked':''}></label><p>${t('settings.notificationsHint')}</p><button data-action="save-settings" data-testid="save-settings">${t('common.save')}</button></section><small data-testid="settings-operator">${t('settings.operatorNote',{name:state.operator==='robin'?'Robin':'Amal'})}</small>`;
}
