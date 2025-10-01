from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("library.db")

# ---- KẾT NỐI DB ----
SCHEMA_READY = False  # chỉ init/migrate một lần mỗi lần app khởi động

def get_db():
    db = getattr(g, "db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db

        global SCHEMA_READY
        if not SCHEMA_READY:
            ensure_schema(db)   # tạo bảng, migrate cột, seed mẫu
            SCHEMA_READY = True
    return db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
# ---- SCHEMA & SEED ----
def ensure_schema(db: sqlite3.Connection):
    # bảng sách
    db.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)
    # bảng mượn
    db.execute("""
        CREATE TABLE IF NOT EXISTS loans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            borrower_name TEXT NOT NULL,
            borrowed_at TEXT NOT NULL,
            due_at TEXT NOT NULL,
            returned_at TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    """)

    # migrate cột mới cho bảng books (nếu thiếu)
    cols = [r["name"] for r in db.execute("PRAGMA table_info(books)").fetchall()]
    if "shelf_code" not in cols:
        db.execute("ALTER TABLE books ADD COLUMN shelf_code TEXT")
    if "location_url" not in cols:
        db.execute("ALTER TABLE books ADD COLUMN location_url TEXT")

    # seed nếu trống
    count = db.execute("SELECT COUNT(*) AS c FROM books").fetchone()["c"]
    if count == 0:
        db.executemany(
            "INSERT INTO books(title, author, year, shelf_code, location_url) VALUES (?,?,?,?,?)",
            [
                ("Clean Code", "Robert C. Martin", 2008, None, None),
                ("The Pragmatic Programmer", "Andrew Hunt", 1999, None, None),
            ],
        )

    # --- CHỈ tạo UNIQUE index khi KHÔNG còn dữ liệu trùng ---
    has_dupes = db.execute("""
        SELECT 1
        FROM (
            SELECT title, author, year, COUNT(*) AS c
            FROM books
            GROUP BY title, author, year
            HAVING c > 1
        ) LIMIT 1
    """).fetchone() is not None

    if not has_dupes:
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_books_unique "
            "ON books(title, author, year)"
        )

    db.commit()

# ---- HELPERS ----
def get_current_loan(db, book_id: int):
    """Loan hiện tại (chưa trả) của 1 sách hoặc None."""
    return db.execute(
        "SELECT id, borrower_name, borrowed_at, due_at "
        "FROM loans WHERE book_id=? AND returned_at IS NULL "
        "ORDER BY id DESC LIMIT 1",
        (book_id,),
    ).fetchone()

# ---- ROUTES ----
@app.get("/")
def home():
    db = get_db()
    rows = db.execute(
        "SELECT id, title, author, year, shelf_code, location_url FROM books ORDER BY id"
    ).fetchall()

    books = []
    for r in rows:
        b = dict(r)
        loan = get_current_loan(db, r["id"])
        b["current_loan"] = dict(loan) if loan else None
        books.append(b)

    return render_template("home.html", books=books)

@app.post("/books/add")
def add_book():
    title = (request.form.get("title") or "").strip()
    author = (request.form.get("author") or "").strip()
    year_raw = (request.form.get("year") or "").strip()
    shelf_code = (request.form.get("shelf_code") or "").strip() or None
    location_url = (request.form.get("location_url") or "").strip() or None

    try:
        year = int(year_raw)
    except ValueError:
        year = None

    if not title or not author or year is None:
        return "Thiếu dữ liệu hợp lệ", 400

    db = get_db()
    # chặn trùng ở tầng ứng dụng
    exists = db.execute(
        "SELECT 1 FROM books WHERE title=? AND author=? AND year=?",
        (title, author, year),
    ).fetchone()
    if exists:
        return "Sách đã tồn tại (quy ước: title + author + year là một bản duy nhất).", 400

    db.execute(
        "INSERT INTO books(title, author, year, shelf_code, location_url) VALUES (?,?,?,?,?)",
        (title, author, year, shelf_code, location_url),
    )
    db.commit()
    return redirect(url_for("home"))

@app.post("/books/delete/<int:book_id>")
def delete_book(book_id: int):
    db = get_db()
    # không xoá khi đang có loan chưa trả
    if get_current_loan(db, book_id):
        return "Không thể xoá: sách đang được mượn", 400

    db.execute("DELETE FROM loans WHERE book_id=?", (book_id,))
    db.execute("DELETE FROM books WHERE id=?", (book_id,))
    db.commit()
    return redirect(url_for("home"))

@app.post("/loans/borrow/<int:book_id>")
def borrow_book(book_id: int):
    borrower = (request.form.get("borrower_name") or "").strip()
    if not borrower:
        return "Thiếu tên người mượn", 400

    db = get_db()
    if get_current_loan(db, book_id):
        return "Sách đang có người mượn", 400

    now = datetime.now()
    due = now + timedelta(days=14)
    db.execute(
        "INSERT INTO loans(book_id, borrower_name, borrowed_at, due_at) VALUES (?,?,?,?)",
        (book_id, borrower, now.strftime("%Y-%m-%d %H:%M:%S"), due.strftime("%Y-%m-%d")),
    )
    db.commit()
    return redirect(url_for("home"))

@app.post("/loans/return/<int:loan_id>")
def return_book(loan_id: int):
    db = get_db()
    db.execute(
        "UPDATE loans SET returned_at=? WHERE id=? AND returned_at IS NULL",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), loan_id),
    )
    db.commit()
    return redirect(url_for("home"))


