const express = require('express');
const cors = require('cors');                	
const app = express();

app.use(express.json());
app.use(cors({ origin: 'http://localhost:5173' }));  


function normalizeIsbn(s) {
  if (!s) return '';
  return String(s).replace(/[-\s]/g, '').toUpperCase();
}

let books = [
  {
    isbn: '9780143127741', // Sapiens (paperback)
    title: 'Sapiens',
    author: 'Yuval Noah Harari',
    year: 2011,
    available: true,
  },
  {
    isbn: '9780132350884', // Clean Code
    title: 'Clean Code',
    author: 'Robert C. Martin',
    year: 2008,
    available: true,
  },
];

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', time: new Date().toISOString() });
});

app.get('/api/books', (req, res) => {
  const q = (req.query.q || '').toLowerCase();
  const cleanedQ = q.replace(/[-\s]/g, '');
  const data = q
    ? books.filter((b) =>
        b.title.toLowerCase().includes(q) ||
        b.author.toLowerCase().includes(q) ||
        normalizeIsbn(b.isbn).includes(cleanedQ)
      )
    : books;
  res.json(data);
});

app.get('/api/books/:isbn', (req, res) => {
  const key = normalizeIsbn(req.params.isbn);
  const book = books.find((b) => normalizeIsbn(b.isbn) === key);
  if (!book) return res.status(404).json({ error: 'Not found' });
  res.json(book);
});

app.post('/api/books', (req, res) => {
  const { isbn, title, author, year, available } = req.body || {};
  const key = normalizeIsbn(isbn);

  if (!key || !title || !author) {
    return res.status(400).json({ error: 'isbn, title, author là bắt buộc' });
  }
  const exists = books.some((b) => normalizeIsbn(b.isbn) === key);
  if (exists) return res.status(409).json({ error: 'ISBN đã tồn tại' });

  const book = {
    isbn, // giữ nguyên định dạng client gửi (có thể có dấu '-')
    title,
    author,
    year: year ? Number(year) : undefined,
    available: typeof available === 'boolean' ? available : true,
  };
  books.push(book);
  res.status(201).json(book);
});

app.put('/api/books/:isbn', (req, res) => {
  const key = normalizeIsbn(req.params.isbn);
  let idx = books.findIndex((b) => normalizeIsbn(b.isbn) === key);

  const { title, author, year, available } = req.body || {};

  if (idx === -1) {
    if (!title || !author) {
      return res.status(400).json({ error: 'Cần title và author để tạo mới' });
    }
    const book = {
      isbn: req.params.isbn, // dùng chính ISBN trên URL
      title,
      author,
      year: year ? Number(year) : undefined,
      available: typeof available === 'boolean' ? available : true,
    };
    books.push(book);
    return res.status(201).json(book); // 201 Created
  }

  if (title !== undefined) books[idx].title = title;
  if (author !== undefined) books[idx].author = author;
  if (year !== undefined) books[idx].year = Number(year);
  if (available !== undefined) books[idx].available = Boolean(available);

  res.json(books[idx]);
});

app.delete('/api/books/:isbn', (req, res) => {
  const key = normalizeIsbn(req.params.isbn);
  const idx = books.findIndex((b) => normalizeIsbn(b.isbn) === key);
  if (idx === -1) return res.status(404).json({ error: 'Not found' });
  const removed = books.splice(idx, 1)[0];
  res.json(removed);
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server dang chay tai http://localhost:${PORT}`);
});

