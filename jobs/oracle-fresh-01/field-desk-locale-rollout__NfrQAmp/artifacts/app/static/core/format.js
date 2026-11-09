import {state} from './state.js';
export const money = minor => new Intl.NumberFormat(state.locale, {style:'currency',currency:'EUR'}).format(minor/100);
export const number = value => new Intl.NumberFormat(state.locale).format(value);
export function parseAmount(raw, locale = state.locale) {
  let text = String(raw).trim().replace(/[٠-٩]/g, ch => String(ch.charCodeAt(0)-0x660));
  const arabicSeparators = locale === 'ar' && /[٬٫]/.test(text);
  const group = locale === 'de' ? '.' : arabicSeparators ? '٬' : ',';
  const decimal = locale === 'de' ? ',' : arabicSeparators ? '٫' : '.';
  const originalPieces = text.split(decimal);
  if (originalPieces.length > 2) return null;
  const groups = originalPieces[0].split(group);
  if (groups.length > 1 && (!/^\d{1,3}$/.test(groups[0]) || groups.slice(1).some(piece => !/^\d{3}$/.test(piece)))) return null;
  text = text.split(group).join('');
  const pieces = text.split(decimal);
  if (pieces.length > 2 || !/^\d+$/.test(pieces[0]) || (pieces.length===2 && !/^\d{1,2}$/.test(pieces[1]))) return null;
  const minor = Number(pieces[0])*100 + Number((pieces[1] || '').padEnd(2,'0'));
  return Number.isSafeInteger(minor) && minor <= 99999999 ? minor : null;
}
export function inputAmount(minor, locale=state.locale) {
  return new Intl.NumberFormat(locale,{minimumFractionDigits:2,maximumFractionDigits:2,useGrouping:false}).format(minor/100);
}
export function localizeDraft(previousLocale) {
  for (const key of ['budget','amount']) {
    if (!(key in state.form)) continue;
    const minor = parseAmount(state.form[key], state.form.amountLocale || previousLocale);
    if (minor !== null) {state.form[key] = inputAmount(minor); state.form.amountLocale = state.locale;}
  }
}
