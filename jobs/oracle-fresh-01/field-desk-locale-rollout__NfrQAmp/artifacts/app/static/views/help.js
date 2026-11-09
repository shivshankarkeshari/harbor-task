import {t} from '../core/locale.js';
export function render() {
  const topics = [t('help.orders'),t('help.dispatch'),t('help.parts'),t('help.billing'),t('help.export')];
  return `<h2 data-testid="page-title">${t('help.title')}</h2><p>${t('help.subtitle')}</p><ul class="help-list">${topics.map(text=>`<li>${text}</li>`).join('')}</ul><button data-action="copy-help" data-testid="copy-help">${t('help.copy')}</button><p data-testid="help-copy-result"></p>`;
}
