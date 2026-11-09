export const money=minor=>new Intl.NumberFormat('en',{style:'currency',currency:'EUR'}).format(minor/100);
export const number=value=>new Intl.NumberFormat('en').format(value);
export function parseAmount(raw) {
  const text=String(raw).trim().replace(/,/g,'');
  return /^\d+(?:\.\d{1,2})?$/.test(text)?Math.round(Number(text)*100):null;
}
export function inputAmount(minor) {return (minor/100).toFixed(2);}
