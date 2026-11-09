import {state} from './state.js';
import {intlTag} from './locale.js';
const MAX_MINOR = 99999999;
const MARKS = /[\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069]/g;
export const money = (minor, locale=state.locale) =>
  new Intl.NumberFormat(intlTag(locale), {style:'currency', currency:'EUR'}).format(minor / 100);
export const number = (value, locale=state.locale) => new Intl.NumberFormat(intlTag(locale)).format(value);
export function asciiDigits(text) {
  return String(text).replace(/[٠-٩]/g, ch => String(ch.charCodeAt(0) - 0x660))
    .replace(/[۰-۹]/g, ch => String(ch.charCodeAt(0) - 0x6f0));
}
// Grouping and decimal separators accepted per locale (sets are disjoint so input is unambiguous).
const SEPARATORS = {
  en: {group: [','], decimal: ['.']},
  de: {group: ['.'], decimal: [',']},
  ar: {group: ['٬', ','], decimal: ['٫', '.']},
};
/** Parse a locale-formatted euro amount into integer cents, or null when malformed/out of range. */
export function parseAmount(raw, locale=state.locale) {
  const separators = SEPARATORS[locale] || SEPARATORS.en;
  let text = asciiDigits(String(raw ?? '').replace(MARKS, '').trim());
  text = [...text].map(ch => separators.group.includes(ch) ? 'G' : separators.decimal.includes(ch) ? 'D' : ch).join('');
  const match = /^(\d{1,3}(?:G\d{3})+|\d+)(?:D(\d{1,2}))?$/.exec(text);
  if (!match) return null;
  const whole = match[1].replace(/G/g, '').replace(/^0+(?=\d)/, '');
  if (whole.length > 6) return null;
  const minor = Number(whole) * 100 + Number((match[2] || '').padEnd(2, '0'));
  return minor <= MAX_MINOR ? minor : null;
}
/** Format integer cents for an editable amount field in the given locale (no grouping). */
export function inputAmount(minor, locale=state.locale) {
  return new Intl.NumberFormat(intlTag(locale), {minimumFractionDigits:2, maximumFractionDigits:2, useGrouping:false})
    .format(minor / 100).replace(MARKS, '');
}
/** Parse a positive-or-zero whole quantity, accepting Arabic-Indic digits; null when malformed. */
export function parseWhole(raw) {
  const text = asciiDigits(String(raw ?? '').replace(MARKS, '').trim());
  return /^\d+$/.test(text) ? Number(text) : null;
}
