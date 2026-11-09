import {state, escape} from './state.js';
export const LOCALES = ['en','de','ar'];
export const RTL = new Set(['ar']);
export const catalogs = {};
export async function loadCatalogs() {
  await Promise.all(LOCALES.map(async locale => {catalogs[locale] = await (await fetch(`/locales/${locale}.json`)).json();}));
}
export const supported = locale => LOCALES.includes(locale);
/** BCP 47 tag used for Intl formatting; Arabic uses Arabic-Indic digits consistently across engines. */
export const intlTag = (locale=state.locale) => locale === 'ar' ? 'ar-u-nu-arab' : locale;
export const isRtl = (locale=state.locale) => RTL.has(locale);
const FSI = '\u2068', PDI = '\u2069';
export function t(key, args={}, locale=state.locale) {
  if (!supported(locale)) locale = 'en';
  let text = catalogs[locale]?.[key] ?? catalogs.en?.[key];
  if (text === undefined) return key;
  if (typeof text === 'object') {
    const count = Number(args?.count);
    text = text[new Intl.PluralRules(locale).select(Number.isFinite(count) ? count : 0)] ?? text.other;
  }
  return text.replace(/\{(\w+)\}/g, (_, name) => {
    const value = args?.[name];
    if (typeof value === 'number') return new Intl.NumberFormat(intlTag(locale)).format(value);
    if (value === undefined || value === null) return `{${name}}`;
    // Isolate user/domain data so Latin text does not reorder the surrounding RTL sentence.
    return isRtl(locale) ? FSI + String(value) + PDI : String(value);
  });
}
/** HTML-escaped translation, for use inside template markup. */
export const te = (key, args={}) => escape(t(key, args));
export function applyDirection() {
  document.documentElement.lang = state.locale;
  document.documentElement.dir = isRtl() ? 'rtl' : 'ltr';
}
export function setLanguage(locale) {
  state.locale = supported(locale) ? locale : 'en';
  applyDirection();
}
export function errorText(error) {
  const code = error?.code && catalogs.en[`error.${error.code}`] !== undefined ? error.code : 'REQUEST_FAILED';
  return t(`error.${code}`, typeof error === 'object' && error ? error : {});
}
