import {state} from './state.js';

function formatter(options={}, locale=state.locale) {
  return new Intl.NumberFormat(locale,{...options,...(locale==='ar'?{numberingSystem:'arab'}:{})});
}
export const money=minor=>formatter({style:'currency',currency:'EUR'}).format(minor/100);
export const number=value=>formatter().format(value);
const digits = raw => String(raw).replace(/[٠-٩]/g,ch=>String(ch.charCodeAt(0)-0x660));

// Validate grouping and fraction length before converting to integer cents.
export function parseAmount(raw, locale=state.locale) {
  let text=digits(raw).trim();
  const separators={en:[',','.'],de:['.',','],ar:['٬','٫']};
  const [group,decimal]=separators[locale] || separators.en;
  const escape=part=>part.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const integer=`(?:[0-9]+|[0-9]{1,3}(?:${escape(group)}[0-9]{3})+)`;
  if (!new RegExp(`^${integer}(?:${escape(decimal)}[0-9]{1,2})?$`).test(text)) return null;
  text=text.split(group).join('');
  const [whole,fraction='']=text.split(decimal);
  const cents=Number(whole)*100+Number(fraction.padEnd(2,'0'));
  return Number.isSafeInteger(cents) && cents<=99999999 ? cents : null;
}
export function inputAmount(minor, locale=state.locale) {
  return formatter({useGrouping:false,minimumFractionDigits:2,maximumFractionDigits:2},locale).format(minor/100);
}
export function translateAmountDraft(locale) {
  for (const field of ['budget','amount']) {
    if (state.form[field]===undefined) continue;
    const previous=state.form.amountLocale || state.locale;
    const cents=parseAmount(state.form[field],previous);
    // Keep invalid drafts verbatim and retain their syntax until the user edits them.
    if (cents!==null) {
      state.form[field]=inputAmount(cents,locale);
      state.form.amountLocale=locale;
    }
  }
}
