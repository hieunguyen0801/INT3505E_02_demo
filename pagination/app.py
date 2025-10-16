from flask import Flask, request, jsonify
import base64, json
from datetime import datetime, timedelta

app = Flask(__name__)

# ----- Seed dữ liệu giả (500 bản ghi) -----
def seed_books(n=500):
    start = datetime(2010, 1, 1)
    data = []
    for i in range(1, n+1):
        pub = start + timedelta(days=i)
        data.append({
            "id": i,
            "isbn": f"978-1-4028-{1000+i}",
            "title": f"Book #{i}",
            "author": f"Author {((i-1)%20)+1}",
            "publishedAt": pub.strftime("%Y-%m-%d")
        })
    return data

BOOKS = seed_books()
TOTAL = len(BOOKS)

# Luôn sort tăng theo id để phân trang ổn định
def sorted_books():
    return sorted(BOOKS, key=lambda b: b["id"])

# ----- Helpers cho cursor -----
def encode_cursor(obj: dict) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")

def decode_cursor(cur: str) -> dict | None:
    try:
        raw = base64.urlsafe_b64decode(cur.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

# ----- 1) Offset/Limit -----
@app.get("/api/books.offset")
def list_books_offset():
    try:
        offset = int(request.args.get("offset", 0))
        limit  = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "offset/limit phải là số nguyên"}), 400

    # Guardrails
    if offset < 0: offset = 0
    if limit < 1:  limit = 1
    if limit > 100: limit = 100  # chặn limit quá lớn

    data = sorted_books()
    slice_ = data[offset: offset+limit]

    return jsonify({
        "items": slice_,
        "pageInfo": {
            "strategy": "offset",
            "offset": offset,
            "limit": limit,
            "total": TOTAL,
            "hasMore": (offset + limit) < TOTAL
        },
        "_links": {
            "self":   {"href": f"/api/books.offset?offset={offset}&limit={limit}"},
            "next":   {"href": f"/api/books.offset?offset={offset+limit}&limit={limit}"} if (offset+limit)<TOTAL else None,
            "first":  {"href": f"/api/books.offset?offset=0&limit={limit}"},
        }
    })
# ----- 2) Page-based (page/size) -----
@app.get("/api/books.page")
def list_books_page():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 20))
    except ValueError:
        return jsonify({"error": "page/size phải là số nguyên"}), 400

    if page < 1: page = 1
    if size < 1: size = 1
    if size > 100: size = 100

    offset = (page - 1) * size
    data = sorted_books()
    slice_ = data[offset: offset+size]
    total_pages = (TOTAL + size - 1) // size

    return jsonify({
        "items": slice_,
        "pageInfo": {
            "strategy": "page",
            "page": page,
            "size": size,
            "total": TOTAL,
            "totalPages": total_pages,
            "hasMore": page < total_pages
        },
        "_links": {
            "self":  {"href": f"/api/books.page?page={page}&size={size}"},
            "next":  {"href": f"/api/books.page?page={page+1}&size={size}"} if page < total_pages else None,
            "prev":  {"href": f"/api/books.page?page={page-1}&size={size}"} if page > 1 else None,
            "first": {"href": f"/api/books.page?page=1&size={size}"},
            "last":  {"href": f"/api/books.page?page={total_pages}&size={size}"}
        }
    })

# ----- 3) Cursor-based -----
# Quy ước: sort theo id tăng; cursor chứa {"afterId": <id cuối trang trước>}
@app.get("/api/books.cursor")
def list_books_cursor():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "limit phải là số nguyên"}), 400

    if limit < 1: limit = 1
    if limit > 100: limit = 100

    cursor = request.args.get("cursor")
    after_id = 0
    if cursor:
        obj = decode_cursor(cursor)
        if not obj or "afterId" not in obj or not isinstance(obj["afterId"], int):
            return jsonify({"error": "cursor không hợp lệ"}), 400
        after_id = obj["afterId"]

    data = sorted_books()
    # Lấy các phần tử có id > after_id
    filtered = [b for b in data if b["id"] > after_id]
    slice_ = filtered[:limit]

    # Tính nextCursor
    if len(slice_) == limit and slice_:
        next_cursor = encode_cursor({"afterId": slice_[-1]["id"]})
    else:
        next_cursor = None

    return jsonify({
        "items": slice_,
        "pageInfo": {
            "strategy": "cursor",
            "limit": limit,
            "hasMore": next_cursor is not None
        },
        "nextCursor": next_cursor
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)