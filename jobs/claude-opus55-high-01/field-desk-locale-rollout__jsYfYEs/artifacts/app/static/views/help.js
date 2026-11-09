import {state} from '../core/state.js';
import {te} from '../core/locale.js';
export function render() {
  const topics = ['orders','dispatch','parts','billing','export'];
  return `<h2 data-testid="page-title">${te('help.title')}</h2><p>${te('help.subtitle')}</p><ul class="help-list">${topics.map(key=>`<li>${te(`help.${key}`)}</li>`).join('')}</ul><button data-action="copy-help" data-testid="copy-help">${te('help.copy')}</button><p data-testid="help-copy-result" role="status">${state.helpCopied?te('common.copied'):''}</p>`;
}
