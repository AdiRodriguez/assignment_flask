
# WHEN RUNNING, IT'S IN JSON!
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, jsonify, request
from datetime import date, timedelta
import json
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)


db = SQLAlchemy(app)

# ----------DATABASE SECTION----------

#Customers table:
class customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    city = db.Column(db.String(80))
    age = db.Column(db.Integer())
    
    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'age': self.age,
        }

#Books table:
class book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    author = db.Column(db.String())
    year_published = db.Column(db.String())
    _type = db.Column("type", db.Integer())

    def __init__(self, name, author, year_published, _type):
        self.name = name
        self.author = author
        self.year_published = year_published
        self._type = _type

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "year_published": self.year_published,
            "_type": self._type
        }

#Loans table
class loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    custid = db.Column(db.Integer, db.ForeignKey('customers.id'))
    bookid = db.Column(db.Integer, db.ForeignKey('books.id'))
    loandate = db.Column(db.Integer())
    returndate = db.Column(db.Integer())

    #Declaring the relationships Loans has with Customers and Books
    customers = db.relationship("customer", backref="cloans")
    books = db.relationship("book", backref="bloans")

    def __init__(self, custid, bookid, loandate, returndate):
        self.custid = custid
        self.bookid = bookid
        self.loandate = loandate
        self.returndate = returndate

    def to_dict(self):
        return {
            "id": self.id,
            "custid": self.custid,
            "bookid": self.bookid,
            "loandate": self.loandate,
            "returndate": self.returndate
        }
# ----------DATABASE END----------

#The funny
@app.route("/")
def menu():
    return "hello we've been trying to reach you about your car's extended warranty"


# ----------CUSTOMERS SECTION----------
#Converts all the customers objects into a single JSON format
@app.route("/customers/view")
def view_customer_S():
    customers_list = [customers.to_dict() for customers in customer.query.all()]
    customers_as_json_data = json.dumps(customers_list)
    return customers_as_json_data

#Converts a single customer object into a JSON format
@app.route("/customers/view/<id>")
def view_customer(id):
    this_customer = customer.query.get(id)
    customer_to_dict = this_customer.to_dict()
    return jsonify(customer_to_dict)



#Creates a new customer profile with users input
@app.route('/customers/new', methods=['POST'])
def new_customer():
    data = request.get_json()
    name = data['name'].title()
    city = data['city'].title()
    age = data['age']

    new_customer = customer(name, city, age)
    db.session.add(new_customer)
    db.session.commit()
    return "A new customer was added."

#Deletes a customer profile
@app.route("/customers/del/<id>", methods=['DELETE'])
def delete_customer(id):
    customer_id = db.get_or_404(customer, id)
    db.session.delete(customer_id)
    db.session.commit()
    return "customer deleted."

#Updates a customer profile
@app.route("/customers/update/<id>", methods=['PUT'])
def upd_customer(id):
    our_book = customer.query.get(id)
    data = request.get_json()
    our_book.name = data["name"].title()
    our_book.autour = data["city"].title()
    our_book.age = data["age"]
    db.session.commit()
    return "updated customer."

# ----------CUSTOMERS END----------


# ----------BOOKS SECTION----------
#Converts all the books objects into a single JSON format
@app.route("/books/view")
def view_book_S():
    books_list = [books.to_dict() for books in book.query.all()]
    books_as_json_data = json.dumps(books_list)
    return books_as_json_data

#Converts a single book object into a JSON format
@app.route("/books/view/<id>")
def view_book(id):
    this_book = book.query.get(id)
    book_to_dict = this_book.to_dict()
    return jsonify(book_to_dict)

#Creates a new book profile with users input
@app.route('/books/new', methods=['POST'])
def new_book():
    data = request.get_json()
    name = data['name'].title()
    author = data['author'].title()
    year_published = data['year_published']
    _type = data["_type"]

    new_book = book(name, author, year_published, _type)
    db.session.add(new_book)
    db.session.commit()
    return "A new book was added."

#Deletes a book profile from the database
@app.route("/books/del/<id>", methods=['DELETE'])
def delete_book(id):
    book_id = db.get_or_404(book, id)
    db.session.delete(book_id)
    db.session.commit()
    return "book deleted."

#Updates a book profile
@app.route("/books/update/<id>", methods=['PUT'])
def upd_book(id):
    our_book = book.query.get(id)
    data = request.get_json()
    our_book.name = data["name"]
    our_book.author = data["author"]
    our_book.year_published = data["year_published"]
    our_book._type = data["_type"]
    db.session.commit()
    return "book updated."
# ----------BOOKS END----------

# ----------LOANS SECTION----------
#Converts all the loans objects into a single JSON format
@app.route("/loans/view")
def view_loan_S():
    loan_list = [loan.to_dict() for loan in loan.query.all()]
    loans_as_json_data = json.dumps(loan_list)
    return loans_as_json_data


#Converts all the late loans objects into a single JSON format
@app.route('/loans/view/late')
def view_late_loan_S(): 
    loan_list = [loan.to_dict() for loan in loan.query.all()]
    late_loan_list = []
    for loann in loan_list:
        get_loan_date = datetime.strptime(loann["loandate"], '%Y-%m-%d')
        get_return_date = datetime.strptime(loann["returndate"], '%Y-%m-%d')
        loandate = datetime.date(get_loan_date)
        returndate = datetime.date(get_return_date)
        if loandate > returndate:
            late_loan_list.append(loann)

    loans_as_json_data = json.dumps(late_loan_list)
    return loans_as_json_data

#Creates a new loan profile with users input
@app.route('/loans/new', methods=['POST'])
def new_loan():
    data = request.get_json()
    custid = data['custid']
    bookid = data['bookid']
    loandate = date.today()
    returndate = loandate + timedelta(days=checktype(data["loan_type"]))
    new_loan = loan(custid, bookid, loandate, returndate)
    db.session.add(new_loan)
    db.session.commit()
    return "added loan."

def checktype(number):
    if int(number) == 1:
        return 10
    elif int(number) == 2:
        return 5
    else:
        return 2
#Deletes a loan profile when user returns a loaned book
@app.route("/loans/del/<id>", methods=['DELETE'])
def return_book(id):
    loan_id = db.get_or_404(loan, id)
    db.session.delete(loan_id)
    db.session.commit()
    return "book deleted."  
# ----------LOANS END---------- 

@app.route('/query', methods=['GET'])
def query_tables():
    # Query the tables
    customers = customer.query.all()
    books = book.query.all()
    loans = loan.query.all()

    # Convert the query results to dictionaries
    customer_dicts = [c.to_dict() for c in customers]
    book_dicts = [b.to_dict() for b in books]
    loan_dicts = [l.to_dict() for l in loans]

    # Create a JSON object
    result = {
        'customers': customer_dicts,
        'books': book_dicts,
        'loans': loan_dicts
    }

    # Convert the JSON object to a JSON string
    json_result = json.dumps(result)

    # Return the JSON response
    return json_result




if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)

