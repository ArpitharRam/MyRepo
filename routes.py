from flask import Blueprint, request, jsonify
from models import db, Author, Book
from datetime import datetime
from flask_migrate import Migrate

library_bp = Blueprint('library', __name__)


@library_bp.route('/authors/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_author(id):
    author = Author.query.get(id)
    if not author:
        return jsonify({'message': 'Author not found'}), 404

    if request.method == 'GET':
        return jsonify({'id': author.id, 'name': author.name})

    if request.method == 'PUT':
        data = request.get_json()
        author.name = data.get('name', author.name)
        db.session.commit()
        return jsonify({'message': 'Author updated successfully'})

    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted successfully'})


@library_bp.route('/authors', methods=['GET', 'POST'])
def handle_authors():
    if request.method == 'GET':
        if request.method == 'POST':
         author = Author.query.first()  # Fetch only one author
         if not author:
            return jsonify({'message': 'No authors found'}), 404
         return jsonify({'id': author.id, 'name': author.name})

    # Handling POST request (Add a new author)
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'message': 'Missing name field'}), 400

    existing_author = Author.query.filter_by(name=data['name']).first()  # Check if author exists
    if existing_author:
        return jsonify({'message': 'Author already exists', 'id': existing_author.id}), 409  # Conflict

    new_author = Author(name=data['name'])
    db.session.add(new_author)
    db.session.commit()
    return jsonify({'message': 'Author added successfully', 'id': new_author.id}), 201


@library_bp.route('/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'title': book.title,
            'published_year': book.published_year,
            'author': book.author.name
        })

    if request.method == 'PUT':
        data = request.get_json()
        book.title = data.get('title', book.title)

        # Validate and update published_year
        if 'published_year' in data:
            try:
                book.published_year = datetime.strptime(str(data['published_year']), '%Y').year
            except ValueError:
                return jsonify({'message': 'Invalid published_year format. Use YYYY'}), 400

        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'})


@library_bp.route('/books', methods=['GET', 'POST'])
def handle_books():
    if request.method == 'GET':
        books = Book.query.all()
        return jsonify([
            {'id': book.id, 'title': book.title, 'published_year': book.published_year, 'author': book.author.name}
            for book in books
        ])

    data = request.get_json()

    # Validate required fields
    if not data or 'title' not in data or 'published_year' not in data or 'author_id' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    # Validate published_year
    try:
        published_year = datetime.strptime(str(data['published_year']), '%Y').year  # Ensures it's a valid year
    except ValueError:
        return jsonify({'message': 'Invalid published_year format. Use YYYY'}), 400

    # Check if author exists
    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'message': 'Author not found'}), 404

    # Create new book
    new_book = Book(
        title=data['title'],
        published_year=published_year,  # Store as integer
        author_id=data['author_id']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully', 'id': new_book.id}), 201.