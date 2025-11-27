from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# "CSDL" giả lập trong bộ nhớ
books = {
    "b1": {"id": "b1", "title": "Lập trình Python cơ bản", "author": "A. Nguyen", "available": True},
    "b2": {"id": "b2", "title": "Kiến trúc REST", "author": "B. Tran", "available": True},
}
loans = {}  # loan_id -> loan
_next_book = 3
_next_loan = 1

@app.get("/books")
def list_books():
    return jsonify(list(books.values())), 200

@app.post("/books")
def add_book():
    global _next_book
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title"); author = data.get("author")
    if not title or not author:
        return jsonify({"error": "Thiếu 'title' hoặc 'author'"}), 400
    book_id = f"b{_next_book}"; _next_book += 1
    books[book_id] = {"id": book_id, "title": title, "author": author, "available": True}
    return jsonify(books[book_id]), 201

@app.post("/borrow")
def borrow_book():
    global _next_loan
    data = request.get_json(force=True, silent=True) or {}
    book_id = data.get("book_id"); user = data.get("user")
    if not book_id or not user:
        return jsonify({"error": "Thiếu 'book_id' hoặc 'user'"}), 400
    book = books.get(book_id)
    if not book:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    if not book["available"]:
        return jsonify({"error": "Sách đang được mượn"}), 409
    book["available"] = False
    loan_id = f"l{_next_loan}"; _next_loan += 1
    loans[loan_id] = {"id": loan_id, "book_id": book_id, "user": user, "returned": False}
    return jsonify(loans[loan_id]), 201

@app.post("/return")
def return_book():
    data = request.get_json(force=True, silent=True) or {}
    loan_id = data.get("loan_id")
    if not loan_id:
        return jsonify({"error": "Thiếu 'loan_id'"}), 400
    loan = loans.get(loan_id)
    if not loan:
        return jsonify({"error": "Không tìm thấy giao dịch mượn"}), 404
    if loan["returned"]:
        return jsonify({"message": "Đã trả trước đó"}), 200
    loan["returned"] = True
    books[loan["book_id"]]["available"] = True
    return jsonify({"message": "Trả sách thành công", "loan": loan}), 200

if __name__ == "__main__":
    app.run(debug=True)
