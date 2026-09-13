const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const token = () => localStorage.getItem('cryptowatch_token');
export const clearSession = () => { localStorage.removeItem('cryptowatch_token'); localStorage.removeItem('cryptowatch_user'); };

export async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token()) headers.Authorization = `Bearer ${token()}`;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 401) clearSession();
    throw new Error(data.detail || 'Something went wrong. Please try again.');
  }
  return data;
}
