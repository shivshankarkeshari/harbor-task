import {state, api} from './state.js';
export const catalogs = {};
export async function loadCatalogs() {
  for (const locale of ['en','de','ar']) catalogs[locale] = await (await fetch(`/locales/${locale}.json`)).json();
}
export function t(key, args = {}) {
  let text = catalogs[state.locale]?.[key] ?? catalogs.en[key];
  if (typeof text === 'object') text = text[new Intl.PluralRules(state.locale).select(args.count)] ?? text.other;
  if (typeof text !== 'string') throw new Error(`Missing UI message: ${key}`);
  return text.replace(/\{(\w+)\}/g, (_, name) => typeof args[name] === 'number'
    ? new Intl.NumberFormat(state.locale).format(args[name]) : String(args[name] ?? `{${name}}`));
}
export function applyDirection() {
  document.documentElement.lang = state.locale;
  document.documentElement.dir = state.locale === 'ar' ? 'rtl' : 'ltr';
}
export async function setLanguage(locale) {
  if (!catalogs[locale]) return;
  await api('preferences', {locale, notifications: state.data.preferences.notifications});
  state.data.preferences.locale = locale;
  state.locale = locale;
  applyDirection();
}
export function errorText(error) {
  return t(`error.${error?.code || 'REQUEST_FAILED'}`, error || {});
}
