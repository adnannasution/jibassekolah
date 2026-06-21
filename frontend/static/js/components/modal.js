/**
 * Modal — dialog generik. Dipakai untuk form tambah/edit di semua modul.
 */
class Modal {
  static open({ title, bodyHtml, onSubmit, submitLabel = 'Simpan', size = '' }) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal ${size === 'lg' ? 'modal--lg' : ''}">
        <div class="modal__header">
          <h2>${title}</h2>
          <button class="modal__close" type="button">&times;</button>
        </div>
        <form class="modal-form">
          <div class="modal__body">${bodyHtml}</div>
          <div class="modal__footer">
            <button type="button" class="btn btn-outline" data-action="batal">Batal</button>
            <button type="submit" class="btn btn-primary">${submitLabel}</button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(overlay);

    const close = () => overlay.remove();
    overlay.querySelector('.modal__close').addEventListener('click', close);
    overlay.querySelector('[data-action="batal"]').addEventListener('click', close);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });

    const form = overlay.querySelector('.modal-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      try {
        await onSubmit(FormBuilder.collect(form), close);
      } catch (err) {
        Modal.showError(form, err.message);
      } finally {
        submitBtn.disabled = false;
      }
    });

    return { close };
  }

  static showError(form, message) {
    let el = form.querySelector('.modal-error');
    if (!el) {
      el = document.createElement('div');
      el.className = 'modal-error';
      el.style.cssText = 'color: var(--color-danger); font-size: var(--text-sm); padding: 0 var(--space-4);';
      form.querySelector('.modal__body').appendChild(el);
    }
    el.textContent = message;
  }

  static confirm(message) {
    return window.confirm(message);
  }

  static alert(message, title = 'Pemberitahuan') {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'modal-overlay';
      overlay.innerHTML = `
        <div class="modal" style="max-width: 380px;">
          <div class="modal__header">
            <h2>${title}</h2>
            <button class="modal__close" type="button">&times;</button>
          </div>
          <div class="modal__body">${message}</div>
          <div class="modal__footer">
            <button type="button" class="btn btn-primary" data-action="ok">OK</button>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);

      const close = () => {
        overlay.remove();
        resolve();
      };
      overlay.querySelector('.modal__close').addEventListener('click', close);
      overlay.querySelector('[data-action="ok"]').addEventListener('click', close);
      overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
    });
  }
}
