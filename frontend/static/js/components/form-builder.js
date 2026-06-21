/**
 * FormBuilder — generate form dari definisi field, dipakai di dalam Modal.
 *
 * fields: [{ name, label, type: 'text'|'number'|'date'|'select'|'uang'|'textarea'|'checkbox',
 *            options?: [{value,label}], required?: bool, value?: any }]
 */
class FormBuilder {
  static render(fields) {
    return fields.map(f => {
      const required = f.required ? 'required' : '';
      const value = f.value ?? '';

      if (f.type === 'select') {
        const opts = (f.options || []).map(o =>
          `<option value="${o.value}" ${String(o.value) === String(value) ? 'selected' : ''}>${o.label}</option>`
        ).join('');
        return `
          <div class="form-group">
            <label for="f_${f.name}">${f.label}</label>
            <select id="f_${f.name}" name="${f.name}" ${required}>
              <option value="">-- pilih --</option>${opts}
            </select>
          </div>`;
      }

      if (f.type === 'checkbox') {
        const checked = value ? 'checked' : '';
        return `
          <div class="form-group form-group--checkbox">
            <label for="f_${f.name}">
              <input id="f_${f.name}" name="${f.name}" type="checkbox" value="true" ${checked} />
              ${f.label}
            </label>
          </div>`;
      }

      if (f.type === 'textarea') {
        return `
          <div class="form-group">
            <label for="f_${f.name}">${f.label}</label>
            <textarea id="f_${f.name}" name="${f.name}" rows="3" ${required}>${value}</textarea>
          </div>`;
      }

      const inputType = f.type === 'uang' ? 'number' : (f.type || 'text');
      const cls = f.type === 'uang' ? 'uang-input' : '';
      return `
        <div class="form-group">
          <label for="f_${f.name}">${f.label}</label>
          <input class="${cls}" id="f_${f.name}" name="${f.name}" type="${inputType}"
                 value="${value}" ${required} ${f.type === 'uang' ? 'step="100" min="0"' : ''} />
        </div>`;
    }).join('');
  }

  /** Ambil semua nilai field dari sebuah <form> jadi object plain. */
  static collect(formEl) {
    const data = new FormData(formEl);
    const result = Object.fromEntries(data.entries());
    formEl.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      result[cb.name] = cb.checked;
    });
    return result;
  }
}
