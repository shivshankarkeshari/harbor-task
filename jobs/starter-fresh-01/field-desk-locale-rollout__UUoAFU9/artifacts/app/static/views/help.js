import {t} from '../core/locale.js';
export function render() {
  const topics = ["Create or edit a work order without losing customer text.","Unavailable crews cannot receive assignments.","Stock reservations require a positive whole quantity.","Charges are stored as integer cents, regardless of language.","Exported CSV uses the same machine format in every language."];
  return `<h2 data-testid="page-title">Using Field Desk</h2><p>A short guide to the operational workflow.</p><ul class="help-list">${topics.map(text=>`<li>${text}</li>`).join('')}</ul><button data-action="copy-help" data-testid="copy-help">Copy quick guide</button><p data-testid="help-copy-result"></p>`;
}
