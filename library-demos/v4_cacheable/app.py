import hashlib, json, time
from flask import Flask, request, jsonify, url_for, make_response

app = Flask(__name__)
DEMO_TOKEN = "demo-token"

books = {
    "b1": {"id": "b1", "title": "Lập trình Python cơ bản", "author": "A. Nguyen", "available": True, "updated_at": time.time()},
    "b2": {"id": "b2", "title": "Kiến trúc REST", "author": "B. Tran", "available": True, "updated_at": time.time()},
}
loans = {}
_next_book = 3
_next_loan = 1
idemp_store = {}

def auth_required():
    auth = request.headers.get("Authorization","")
    return auth == f"Bearer {DEMO_TOKEN}"

@app.before_request
def _auth():
    if request.path.startswith("/health"):
        return
    if not auth_required():
        return jsonify({"error":"Unauthorized"}), 401

def wrap(data, links=None):
    doc = {"data": data}
    if links: doc["links"] = links
    return doc

def etag_for(obj) -> str:
    # Tạo ETag ổn định từ dữ liệu
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def set_cache_headers(resp, max_age=30, etag=None):
    resp.headers["Cache-Control"] = f"public, max-age={max_age}"
    if etag: resp.headers["ETag"] = etag

def conditional_etag_match(etag: str) -> bool:
    inm = request.headers.get("If-None-Match")
    return inm is not None and inm == etag

def maybe_replay_idempotent():
    key = request.headers.get("Idempotency-Key")
    if key and key in idemp_store:
        cached = idemp_store[key]
        r = make_response(jsonify(cached["body"]), cached["status"])
        for h, v in cached["headers"].items():
            r.headers[h] = v
        return r
    return None

def store_idempotent(resp):
    key = request.headers.get("Idempotency-Key")
    if key:
        idemp_store[key] = {
            "status": resp.status_code,
            "headers": {k: v for k, v in resp.headers.items()},
            "body": resp.get_json()
        }

@app.get("/health")
def health():
    return {"status":"ok"}, 200

@app.get("/books")
def get_books():
    # ETag cho collection dựa trên danh sách sách (id, title, author, available, updated_at)
    listing = list(books.values())
    et = etag_for(listing)
    if conditional_etag_match(et):
        resp = make_response("", 304)
        set_cache_headers(resp, max_age=30, etag=et)
        return resp
    payload = wrap(listing, links={"self": url_for("get_books")})
    resp = make_response(jsonify(payload), 200)
    set_cache_headers(resp, max_age=30, etag=et)
    return resp

@app.post("/books")
def create_book():
    replay = maybe_replay_idempotent()
    if replay: return replay
    global _next_book
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title"); author = data.get("author")
    if not title or not author:
        return jsonify({"error":"Thiếu 'title'/'author'"}), 400
    book_id = f"b{_next_book}"; _next_book += 1
    books[book_id] = {"id": book_id, "title": title, "author": author, "available": True, "updated_at": time.time()}
    loc = url_for("get_book", book_id=book_id)
    resp = make_response(jsonify(wrap(books[book_id], links={"self": loc})), 201)
    resp.headers["Location"] = loc
    store_idempotent(resp)
    return resp

@app.get("/books/<book_id>")
def get_book(book_id):
    b = books.get(book_id)
    if not b:
        return jsonify({"error":"Không tìm thấy sách"}), 404
    et = etag_for(b)
    if conditional_etag_match(et):
        resp = make_response("", 304)
        set_cache_headers(resp, max_age=60, etag=et)
        return resp
    resp = make_response(jsonify(wrap(b, links={"self": url_for("get_book", book_id=book_id)})), 200)
    set_cache_headers(resp, max_age=60, etag=et)
    return resp

@app.patch("/books/<book_id>")
def update_book(book_id):
    b = books.get(book_id)
    if not b:
        return jsonify({"error":"Không tìm thấy sách"}), 404
    data = request.get_json(force=True, silent=True) or {}
    for k in ("title","author","available"):
        if k in data: b[k] = data[k]
    b["updated_at"] = time.time()
    # Khi sửa, ETag thay đổi → client GET lần sau sẽ thấy mới
    return jsonify(wrap(b, links={"self": url_for("get_book", book_id=book_id)})), 200

@app.get("/loans")
def list_loans():
    resp = make_response(jsonify(wrap(list(loans.values()), links={"self": url_for("list_loans")})), 200)
    set_cache_headers(resp, max_age=10)  # loans thường thay đổi nhanh → cache ngắn
    return resp

@app.post("/loans")
def create_loan():
    replay = maybe_replay_idempotent()
    if replay: return replay
    global _next_loan
    data = request.get_json(force=True, silent=True) or {}
    book_id = data.get("book_id"); user = data.get("user")
    if not book_id or not user: return jsonify({"error":"Thiếu 'book_id'/'user'"}), 400
    b = books.get(book_id)
    if not b: return jsonify({"error":"Không tìm thấy sách"}), 404
    if not b["available"]: return jsonify({"error":"Sách đang được mượn"}), 409
    b["available"] = False; b["updated_at"] = time.time()
    loan_id = f"l{_next_loan}"; _next_loan += 1
    loans[loan_id] = {"id": loan_id, "book_id": book_id, "user": user, "returned": False}
    loc = url_for("get_loan", loan_id=loan_id)
    resp = make_response(jsonify(wrap(loans[loan_id], links={"self": loc})), 201)
    resp.headers["Location"] = loc
    store_idempotent(resp)
    return resp

@app.get("/loans/<loan_id>")
def get_loan(loan_id):
    l = loans.get(loan_id)
    if not l: return jsonify({"error":"Không tìm thấy loan"}), 404
    # Loans biến động nhiều → không gắn ETag ở đây (có thể gắn nếu cần)
    resp = make_response(jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200)
    set_cache_headers(resp, max_age=5)
    return resp

@app.patch("/loans/<loan_id>")
def return_loan(loan_id):
    l = loans.get(loan_id)
    if not l: return jsonify({"error":"Không tìm thấy loan"}), 404
    if l["returned"]:
        return jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200
    l["returned"] = True
    books[l["book_id"]]["available"] = True
    books[l["book_id"]]["updated_at"] = time.time()
    return jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200

if __name__ == "__main__":
    app.run(debug=True)
