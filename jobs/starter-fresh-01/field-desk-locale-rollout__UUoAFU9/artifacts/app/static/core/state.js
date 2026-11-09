export const state = {
  operator: localStorage.getItem('field-desk.operator') || 'robin', locale: 'en',
  route: location.hash.slice(1) || 'orders', search: '', filter: 'ALL', selected: [],
  data: null, modal: null, form: {}, error: null, notice: null,
};
export async function api(path, body) {
  const response = await fetch(`/api/${path}`, body === undefined ? {} : {
    method: 'POST', headers: {'Content-Type':'application/json','X-Operator':state.operator},
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw data.error || {code:'REQUEST_FAILED'};
  return data;
}
export async function reload() {
  state.data = await api(`bootstrap?operator=${encodeURIComponent(state.operator)}`);
}
export const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const value = key => escape(state.form[key] ?? '');
