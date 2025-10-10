from flask import Flask, request, jsonify, url_for, make_response

app = Flask(__name__)

books = {
    "b1": {"id": "b1", "title": "Lập trình Python cơ bản", "author": "A. Nguyen", "available": True},
    "b2": {"id": "b2", "title": "Kiến trúc REST", "author": "B. Tran", "available": True},
}
loans = {}
_next_book = 3
_next_loan = 1

def wrap(data, links=None):
    doc = {"data": data}
    if links: doc["links"] = links
    return doc

@app.get("/books")
def get_books():
    items = []
    for b in books.values():
        items.append({**b, "links": {"self": url_for("get_book", book_id=b["id"], _external=False)}})
    return jsonify(wrap(items, links={"self": url_for("get_books")})), 200

@app.post("/books")
def create_book():
    global _next_book
    payload = request.get_json(force=True, silent=True) or {}
    title = payload.get("title"); author = payload.get("author")
    if not title or not author:
        return jsonify({"error": "Thiếu 'title'/'author'"}), 400
    book_id = f"b{_next_book}"; _next_book += 1
    books[book_id] = {"id": book_id, "title": title, "author": author, "available": True}
    location = url_for("get_book", book_id=book_id)
    resp = make_response(jsonify(wrap(books[book_id], links={"self": location})), 201)
    resp.headers["Location"] = location
    return resp

@app.get("/books/<book_id>")
def get_book(book_id):
    b = books.get(book_id)
    if not b:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    return jsonify(wrap(b, links={"self": url_for("get_book", book_id=book_id)})), 200

@app.patch("/books/<book_id>")
@app.put("/books/<book_id>")
def update_book(book_id):
    b = books.get(book_id)
    if not b:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    payload = request.get_json(force=True, silent=True) or {}
    for k in ("title","author","available"):
        if k in payload: b[k] = payload[k]
    return jsonify(wrap(b, links={"self": url_for("get_book", book_id=book_id)})), 200

@app.delete("/books/<book_id>")
def delete_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    if not books[book_id]["available"]:
        return jsonify({"error": "Không thể xoá: sách đang được mượn"}), 409
    del books[book_id]
    return "", 204

@app.get("/loans")
def list_loans():
    items = []
    for l in loans.values():
        items.append({**l, "links": {"self": url_for("get_loan", loan_id=l["id"])}})
    return jsonify(wrap(items, links={"self": url_for("list_loans")})), 200

@app.post("/loans")
def create_loan():
    global _next_loan
    payload = request.get_json(force=True, silent=True) or {}
    book_id = payload.get("book_id"); user = payload.get("user")
    if not book_id or not user: return jsonify({"error":"Thiếu 'book_id'/'user'"}), 400
    b = books.get(book_id)
    if not b: return jsonify({"error":"Không tìm thấy sách"}), 404
    if not b["available"]: return jsonify({"error":"Sách đang được mượn"}), 409
    b["available"] = False
    loan_id = f"l{_next_loan}"; _next_loan += 1
    loans[loan_id] = {"id": loan_id, "book_id": book_id, "user": user, "returned": False}
    location = url_for("get_loan", loan_id=loan_id)
    resp = make_response(jsonify(wrap(loans[loan_id], links={"self": location})), 201)
    resp.headers["Location"] = location
    return resp

@app.get("/loans/<loan_id>")
def get_loan(loan_id):
    l = loans.get(loan_id)
    if not l: return jsonify({"error":"Không tìm thấy"}), 404
    return jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200

@app.patch("/loans/<loan_id>")
def return_loan(loan_id):
    l = loans.get(loan_id)
    if not l: return jsonify({"error":"Không tìm thấy"}), 404
    if l["returned"]:
        return jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200
    l["returned"] = True
    books[l["book_id"]]["available"] = True
    return jsonify(wrap(l, links={"self": url_for("get_loan", loan_id=loan_id)})), 200

if __name__ == "__main__":
    app.run(debug=True)
