/**
 * Router — navigasi SPA berbasis hash (#penerimaan/jenis, dst), tanpa reload.
 * Tiap module didaftarkan sebagai class yang punya method render(container, params).
 * Module SEBELUMNYA otomatis dipanggil destroy()-nya (kalau ada) sebelum module
 * baru di-render, supaya event listener lama gak numpuk / nyangkut (memory leak).
 */
class Router {
  constructor(container, navContainer) {
    this.container = container;
    this.navContainer = navContainer;
    this.routes = {};       // { 'penerimaan': ModuleClass }
    this.currentModule = null;

    window.addEventListener('hashchange', () => this._handleRoute());
  }

  register(path, ModuleClass, label, icon = '') {
    this.routes[path] = { ModuleClass, label, icon };
  }

  start(defaultPath) {
    if (!window.location.hash) {
      window.location.hash = `#${defaultPath}`;
    }
    this._renderNav();
    this._handleRoute();
  }

  navigate(path) {
    window.location.hash = `#${path}`;
  }

  _renderNav() {
    this.navContainer.innerHTML = Object.entries(this.routes)
      .map(([path, { label, icon }]) => `
        <a class="sidebar__link" data-path="${path}" href="#${path}">
          <span>${icon}</span><span>${label}</span>
        </a>
      `).join('');
  }

  _handleRoute() {
    const [path, ...rest] = window.location.hash.replace('#', '').split('/');
    const params = rest;
    const entry = this.routes[path];

    // Update highlight nav aktif
    this.navContainer.querySelectorAll('.sidebar__link').forEach(el => {
      el.classList.toggle('is-active', el.dataset.path === path);
    });

    if (!entry) {
      this.container.innerHTML = `<div class="empty-state">Halaman tidak ditemukan.</div>`;
      return;
    }

    if (this.currentModule && typeof this.currentModule.destroy === 'function') {
      this.currentModule.destroy();
    }

    this.container.innerHTML = '';
    this.currentModule = new entry.ModuleClass(this.container, api, params);
    this.currentModule.render();
  }
}
