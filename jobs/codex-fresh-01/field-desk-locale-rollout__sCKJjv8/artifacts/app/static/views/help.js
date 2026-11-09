import {state} from '../core/state.js';
import {t} from '../core/locale.js';
export function render() {
  const topics = ['orders','dispatch','parts','billing','export'];
  return `<h2 data-testid="page-title">${t('help.title')}</h2><p>${t('help.subtitle')}</p><ul class="help-list">${topics.map(topic=>`<li>${t(`help.${topic}`)}</li>`).join('')}</ul><button data-action="copy-help" data-testid="copy-help">${t('help.copy')}</button><p data-testid="help-copy-result" role="status">${state.helpCopied?t('common.copied'):''}</p>`;
}
