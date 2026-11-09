import {state, api} from './state.js';
import {translateAmountDraft, number} from './format.js';
export const catalogs = {};
export async function loadCatalogs() {
  await Promise.all(['en','de','ar'].map(async locale=>{
    catalogs[locale]=await (await fetch(`/locales/${locale}.json`)).json();
  }));
}
export function t(key, args={}) {
  let text=catalogs[state.locale]?.[key] ?? catalogs.en[key] ?? key;
  if (typeof text==='object') text=text[new Intl.PluralRules(state.locale).select(args.count)] ?? text.other;
  return text.replace(/\{(\w+)\}/g,(_,name)=>typeof args[name]==='number'?number(args[name]):String(args[name]??`{${name}}`));
}
export function applyDirection() {
  document.documentElement.lang=state.locale;
  document.documentElement.dir=state.locale==='ar'?'rtl':'ltr';
}
export async function setLanguage(locale) {
  if (!['en','de','ar'].includes(locale)) throw {code:'LOCALE_INVALID'};
  const operator=state.operator;
  await api('preferences',{locale,notifications:state.data.preferences.notifications});
  if (state.operator!==operator) return;
  translateAmountDraft(locale);
  state.locale=locale;
  state.data.preferences.locale=locale;
  applyDirection();
}
export function errorText(error) {
  const key=`error.${error?.code || 'REQUEST_FAILED'}`;
  return t(catalogs[state.locale]?.[key]?key:'error.REQUEST_FAILED',error || {});
}
