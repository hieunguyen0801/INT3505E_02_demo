// ---- API base config (linh hoạt theo môi trường) ----
function getApiBase() {
  const qs = new URLSearchParams(location.search);
  const fromQS = qs.get('api');                  // ưu tiên ?api=...
  const fromGlobal = typeof window !== 'undefined' ? window.API_BASE : undefined; // từ index.html
  const fallback = location.origin + '/api';     // same-origin nếu deploy chung host
  const base = fromQS || fromGlobal || fallback;
  return String(base).replace(/\/+$/, '');       // bỏ dấu '/' cuối
}
const API_BASE = getApiBase();
const API = `${API_BASE}/books`;
console.log('[Client] API_BASE =', API_BASE);
console.log('[Client] API endpoint =', API);


// ------------------------------------------------------

const $ = (id) => document.getElementById(id);
const tbody = document.querySelector('#tbl tbody');

let editingIsbn = null; // null = chế độ tạo mới

async function fetchBooks(q = '') {
  const url = q ? `${API}?q=${encodeURIComponent(q)}` : API;
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

function renderRows(list) {
  tbody.innerHTML = list.map(b => `
    <tr>
      <td>${b.isbn}</td>
      <td>${b.title}</td>
      <td>${b.author}</td>
      <td>${b.year ?? ''}</td>
      <td>${b.available ? '✅' : '❌'}</td>
      <td>
        <button onclick="startEdit('${b.isbn}')">Sửa</button>
        <button onclick="deleteBook('${b.isbn}')">Xóa</button>
      </td>
    </tr>
  `).join('');
}

async function render(q = '') {
  const data = await fetchBooks(q).catch(err => {
    alert('Không tải được danh sách: ' + err.message);
    return [];
  });
  renderRows(data);
}

async function createBook() {
  const payload = {
    isbn: $('isbn').value.trim(),
    title: $('title').value.trim(),
    author: $('author').value.trim(),
    year: $('year').value ? Number($('year').value) : undefined,
    available: $('available').checked
  };
  if (!payload.isbn || !payload.title || !payload.author) {
    alert('Cần nhập ISBN, Tiêu đề, Tác giả.');
    return;
  }
  const r = await fetch(API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await r.json().catch(() => ({}));
  if (r.status === 201) {
    await render($('search').value.trim());
    clearFormAndMode();
  } else {
    alert(`Lỗi ${r.status}: ${data.error || 'Không rõ'}`);
  }
}

async function startEdit(isbn) {
console.log('[Client] DELETE', `${API}/${encodeURIComponent(isbn)}`);
  const r = await fetch(`${API}/${encodeURIComponent(isbn)}`);
  if (!r.ok) return alert('Không tìm thấy sách.');
  const b = await r.json();

  $('isbn').value = b.isbn;
  $('title').value = b.title || '';
  $('author').value = b.author || '';
  $('year').value = b.year ?? '';
  $('available').checked = !!b.available;

  editingIsbn = b.isbn;
  $('isbn').disabled = true;
  $('btnCreate').disabled = true;
  $('btnUpdate').disabled = false;
  $('isbn').focus();
}

async function updateBook() {
  if (!editingIsbn) return alert('Chưa chọn cuốn nào để sửa.');
  const payload = {
    title: $('title').value.trim(),
    author: $('author').value.trim(),
    year: $('year').value ? Number($('year').value) : undefined,
    available: $('available').checked
  };
console.log('[Client] PUT', `${API}/${encodeURIComponent(editingIsbn)}`, payload);
  const r = await fetch(`${API}/${encodeURIComponent(editingIsbn)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await r.json().catch(() => ({}));
  if (r.ok) {
    await render($('search').value.trim());
    clearFormAndMode();
  } else {
    alert(`Lỗi ${r.status}: ${data.error || 'Không rõ'}`);
  }
}

async function deleteBook(isbn) {
  if (!confirm(`Xóa sách ISBN ${isbn}?`)) return;
console.log('[Client] DELETE', `${API}/${encodeURIComponent(isbn)}`);
  const r = await fetch(`${API}/${encodeURIComponent(isbn)}`, { method: 'DELETE' });
  const data = await r.json().catch(() => ({}));
  if (r.ok) {
    await render($('search').value.trim());
    if (editingIsbn === isbn) clearFormAndMode();
  } else {
    alert(`Lỗi ${r.status}: ${data.error || 'Không rõ'}`);
  }
}

function clearFormAndMode() {
  editingIsbn = null;
  $('isbn').disabled = false;
  $('btnCreate').disabled = false;
  $('btnUpdate').disabled = true;

  $('isbn').value = '';
  $('title').value = '';
  $('author').value = '';
  $('year').value = '';
  $('available').checked = true;
  $('isbn').focus();
}

// Sự kiện
$('btnCreate').addEventListener('click', createBook);
$('btnUpdate').addEventListener('click', updateBook);
$('btnClear').addEventListener('click', clearFormAndMode);
$('btnReload').addEventListener('click', () => render($('search').value.trim()));
$('btnSearch').addEventListener('click', () => render($('search').value.trim()));

// Cho nút trong bảng gọi được
window.startEdit = startEdit;
window.deleteBook = deleteBook;

window.addEventListener('DOMContentLoaded', () => {
  $('btnUpdate').disabled = true;
  render();
});

