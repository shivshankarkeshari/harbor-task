import {state} from './state.js';
export const catalogs = {};
export async function loadCatalogs() {
  for (const locale of ['en','de','ar']) catalogs[locale] = await (await fetch(`/locales/${locale}.json`)).json();
}
export function t(key, args={}) {
  let text=catalogs.en[key];
  if (typeof text==='object') text=text[new Intl.PluralRules('en').select(args.count)] ?? text.other;
  return text.replace(/\{(\w+)\}/g,(_,name)=>typeof args[name]==='number'?new Intl.NumberFormat('en').format(args[name]):String(args[name]??`{${name}}`));
}
export function applyDirection() {
  document.documentElement.lang=state.locale;
  document.documentElement.dir='ltr';
}
export async function setLanguage(locale) {
  state.locale=locale;
  localStorage.setItem('field-desk.locale',locale);
  applyDirection();
}
export function errorText(error) {return t(`error.${error?.code || 'REQUEST_FAILED'}`,error || {});}
