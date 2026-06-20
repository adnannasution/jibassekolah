/**
 * ApiClient — pembungkus fetch terpusat. Semua module manggil lewat sini,
 * jadi kalau mau nambah auth header / error handling global, cukup ubah di satu tempat.
 */
class ApiClient {
  constructor(baseUrl = '/api') {
    this.baseUrl = baseUrl;
  }

  async request(method, path, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    const token = localStorage.getItem('jibas_token');
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body !== undefined) opts.body = JSON.stringify(body);

    const res = await fetch(`${this.baseUrl}${path}`, opts);

    if (!res.ok) {
      let detail = res.statusText;
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch (_) { /* respons bukan JSON, pakai statusText */ }
      throw new Error(detail);
    }

    if (res.status === 204) return null;
    return res.json();
  }

  get(path) { return this.request('GET', path); }
  post(path, body) { return this.request('POST', path, body); }
  put(path, body) { return this.request('PUT', path, body); }
  delete(path) { return this.request('DELETE', path); }
}

const api = new ApiClient();
