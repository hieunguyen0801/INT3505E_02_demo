
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request
from datetime import datetime
from flasgger import Swagger

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.url_map.strict_slashes = False
app.config['SWAGGER'] = {
    'title': 'Library API',
    'uiversion': 3
}
swagger = Swagger(app)
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="available")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'status': self.status
        }

    def __repr__(self):
        return f"<Book {self.title}>"
    
@app.route("/api/books", methods=["GET"])
def get_books():
    """
    Get all books
    ---
    tags:
      - Books
    responses:
      200:
        description: List of all books
        schema:
            type: array
            items:
                type: object
                properties:
                    id:
                        type: integer
                        example: 1
                    title:
                        type: string
                        example: "To Kill a Mockingbird"
                    author:
                        type: string
                        example: "Harper Lee"
                    year:
                        type: integer
                        example: 1960
                    status:
                        type: string
                        example: "available"
    """
    books = Book.query.all()
    data = [book.to_dict() for book in books]
    return jsonify(data), 200

@app.route("/api/books", methods=["POST"])
def create_book():
    """
    Create a new book
    ---
    tags:
      - Books
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - author
            - year
          properties:
            title:
              type: string
              example: "My Side"        
            author:
              type: string
              example: "David Beckham"  
            year:
              type: integer
              example: 2002            
    responses:
      201:
        description: Book created
    """
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')

    new_book = Book(title=title, author=author, year=year)
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201

@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """
    Get a book by ID
    ---
    tags:
      - Books
    parameters:
      - in: path
        name: book_id
        required: true
        type: integer
        description: ID of the book
    responses:
      200:
        description: A single book
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "To Kill a Mockingbird"
            author:
              type: string
              example: "Harper Lee"
            year:
              type: integer
              example: 1960
            status:
              type: string
              example: "available"
      404:
        description: Book not found
        schema:
          type: object
          properties: 
            error:
              type: string
              example: "Book not found"      
    """
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    """
    Update a book by ID
    ---
    tags:
      - Books
    consumes:
      - application/json
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
        description: ID of the book to update   
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "My Side - Updated"
            author:
              type: string
              example: "David Beckham"
            year:
              type: integer
              example: 2003
            status:
              type: string
              example: "available"
    responses:
      200:
        description: Updated book
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            title:
              type: string
              example: "My Side - Updated"
            author:
              type: string
              example: "David Beckham"
            year:
              type: integer
              example: 2003
            status:
              type: string
              example: "available"
      404:
        description: Book not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Book not found"
    """

    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json()
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.year = data.get('year', book.year)
    book.status = data.get('status', book.status)
    db.session.commit()
    return jsonify(book.to_dict()), 200

@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """
    Delete a book by ID
    ---
    tags:
      - Books
    parameters:
      - in: path
        name: book_id
        required: true
        type: integer
        description: ID of the book to delete
    responses:
      200:
        description: Book deleted
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Book deleted"
      404:
        description: Book not found
        schema:
          type: object
          properties: 
            error:
              type: string
              example: "Book not found"
    """
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    borrowed_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    due_at = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'borrowed_at': self.borrowed_at.isoformat() if self.borrowed_at else None,
            'due_at': self.due_at.isoformat() if self.due_at else None,
            'returned_at': self.returned_at.isoformat() if self.returned_at else None, 
        }
@app.route("/api/borrows", methods=["POST"])
def create_borrow():
    """
    Create a new borrow record
    ---
    tags:
      - Borrows
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              example: 1
            book_id:
              type: integer
              example: 1
            due_at:
              type: string
              format: date
              example: "2025-11-27"
              description: Optional, format YYYY-MM-DD
    responses:
      201:
        description: Borrow created
        schema:
          type: object
          properties:
            id: 
              type: integer
              example: 1
            user_id:
              type: integer
              example: 1
            book_id:
              type: integer
              example: 1
            borrowed_at:
              type: string
              format: date-time
              example: "2025-11-20T04:09:26"
            due_at:
              type: string
              format: date-time
              example: "2025-11-27T00:00:00"
            returned_at:
              type: string
              format: date-time
              example: null
      400:
        description: Bad request
        schema:
          type: object
          properties: 
            error:
              type: string
              example: "Book is already borrowed"
      404:
        description: Book not found
        schema:
          type: object
          properties: 
            error:
              type: string
              example: "Book not found"
    """
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    due_at_str = data.get("due_at")
    if user_id is None or book_id is None:
        return jsonify({"error": "required user_id and book_id"}), 400
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    if book.status == "borrowed":
        return jsonify({"error": "Book is already borrowed"}), 400
    if due_at_str:
        try:
            due_at = datetime.strptime(due_at_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid due_at format. Expected YYYY-MM-DD"}), 400
    else:
        due_at = None
    borrow = Borrow(user_id=user_id, book_id=book_id, due_at=due_at)
    book.status = "borrowed"
    db.session.add(borrow)
    db.session.commit()
    return jsonify(borrow.to_dict()), 201

@app.route("/api/borrows", methods=["GET"])
def list_borrows():
    """
    Get all borrows
    ---
    tags:
      - Borrows
    responses:
      200:
        description: List of all borrows
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              user_id:
                type: integer
                example: 1
              book_id:
                type: integer
                example: 1
              borrowed_at:
                type: string
                example: "2025-11-20T04:09:26"
              due_at:
                type: string
                example: "2025-11-27T00:00:00"
              returned_at:
                type: string
                example: null
    """
    borrows = Borrow.query.all()
    data = [borrow.to_dict() for borrow in borrows]
    return jsonify(data), 200

@app.route("/api/borrows/<int:borrow_id>/return", methods=["POST"])
def return_borrow(borrow_id):
    """
    Return a borrowed book
    ---
    tags:
      - Borrows
    parameters:
      - in: path
        name: borrow_id
        required: true
        type: integer
        description: ID of the borrow record
    responses:
      200:
        description: Book returned
        schema:
          type: object
          properties: 
            message:
              type: string
              example: "Book returned"
      400:
        description: Bad request
        schema:
          type: object
          properties:
            message: 
              type: string
              example: "Book already returned"
      404:
        description: Borrow record not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Borrow record not found"
    """
    borrow = Borrow.query.get(borrow_id)
    if borrow is None:
        return jsonify({"error": "Borrow record not found"}), 404
    if borrow.returned_at is not None:
        return jsonify({"error": "Book already returned"}), 400
    book = Book.query.get(borrow.book_id)
    borrow.returned_at = datetime.utcnow()
    book.status = "available"
    db.session.commit()
    return jsonify(message = "Book returned"), 200

def index():
    return "Library API is running."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)