from flask import Flask, redirect, request, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 
from datetime import datetime, timedelta
from sqlalchemy import func
app=Flask(__name__)
app.config['SECRET_KEY']='deepubhai'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
#Models below
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
    Content = db.Column(db.String(100), nullable=False)
    pdf_path = db.Column(db.String(400), nullable=False)
    Quantity=db.Column(db.Integer,default=1, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
user = db.relationship('User', backref=db.backref('books'))

class BookIssued(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    issue_date=db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Not Purchased', nullable=False)

    user = db.relationship('User', backref=db.backref('issues', lazy=True))
    book = db.relationship('Book', backref=db.backref('issues', lazy=True))

class Section(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description=db.Column(db.String(500))
section = db.relationship('Section', backref=db.backref('books'))

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    author=db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='pending', nullable=False)

    user = db.relationship('User', backref=db.backref('requests', lazy=True))
    book = db.relationship('Book', backref=db.backref('requests', lazy=True))

class RatingFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=False)

    book = db.relationship('Book', backref=db.backref('ratings_feedback', lazy=True))
    user = db.relationship('User', backref=db.backref('ratings_feedback', lazy=True))
# -- End of Models --
# User home page and login system
@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User successfully registered!, Please Login to continue')
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose a different one.')
    return render_template('Signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect('/udash')
        else:
            flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')
# user profile page
@app.route('/uprofile')
def uprofile():
    user=User.query.get(session['user_id'])
    books=Book.query.all()
    brq=BookRequest.query.all()
    return render_template('uprofile.html',user=user, books=books,bookrequests=brq)
    

@app.route('/changepassu', methods=['POST'])
def changepassu():
    user=User.query.get(session['user_id'])
    user_password=request.form['user_password']
    user.password = user_password
    db.session.commit()
    return redirect('/uprofile')
# user dashboard page
@app.route('/udash')
def Udash():
    user = User.query.get(session['user_id'])
    sections = Section.query.all()
    books = Book.query.all()
    recent_books = Book.query.filter(Book.date_created >= datetime.utcnow() - timedelta(days=5)).all()
    top_rated_books = db.session.query(Book, func.avg(RatingFeedback.rating).label('avg_rating')) \
                                .join(RatingFeedback, Book.id == RatingFeedback.book_id) \
                                .group_by(Book.id) \
                                .order_by(func.avg(RatingFeedback.rating).desc()) \
                                .all()

    return render_template('Udash.html',books=books,sections=sections,user_id=user.id,current_datetime=datetime.utcnow(), recent_books=recent_books,top_rated_books=top_rated_books)
@app.route('/search')
def search():
    query = request.args.get('query')
    filter_option = request.args.get('filter')
    
    sections = []
    books = []
    
    if filter_option == 'section':
        sections = Section.query.filter(Section.name.ilike(f'%{query}%')).all()
        if sections:
            books = Book.query.filter(Book.section_id.in_([section.id for section in sections])).all()
    elif filter_option == 'book':
        books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()
    elif filter_option == 'author':
        books = Book.query.filter(Book.author.ilike(f'%{query}%')).all()

    return render_template('Search.html', sections=sections, books=books)
        
@app.route('/request_book', methods=['POST'])
def request_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        user_id = session.get('user_id')
        book = Book.query.filter_by(id=book_id).first()
        existing_request = BookRequest.query.filter_by(user_id=user_id, book_id=book_id).first()
        user_request_count = BookRequest.query.filter_by(user_id=user_id).count()

        if user_request_count >= 5:
            flash('You have already made the maximum number of requests (5).', 'error')
            return redirect('/udash')
        if existing_request:
            flash('You have already requested this book.', 'error')
            return redirect('/udash')
        new_request = BookRequest(user_id=user_id, book_id=book_id, name=book.title, author=book.author)
        db.session.add(new_request)
        db.session.commit()
        flash('Book request submitted successfully! Waiting for Librarian to Accept', 'success')
        return redirect('/udash')

    return redirect('/udash')

@app.route('/my_books')
def my_books():
    user_id = session.get('user_id')
    user_issues = BookIssued.query.filter_by(user_id=user_id).all()
    accepted_requests = [issue for issue in user_issues]

    if not accepted_requests:
        flash('You have no accepted book requests.', 'info')
        return render_template('my_books.html')

    books = [Book.query.get(issue.book_id) for issue in accepted_requests]
    return render_template('my_books.html', requested_books=accepted_requests, books=books, bookissued=user_issues)

@app.route('/view_pdf/<path:pdf_path>')
def view_books(pdf_path):
    return render_template('pdf_viewer.html', pdf_path=pdf_path)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    user_id=session.get('user_id')
    card_number = request.form.get('cardNumber')
    expiry_date = request.form.get('expiryDate')
    cvv = request.form.get('cvv')
    book_id = request.form.get('book_id')
    bookissued=BookIssued.query.filter_by(book_id=book_id,user_id=user_id).first()
    if bookissued:
        bookissued.status='Purchased'
        db.session.commit()
    else:
        flash('Book not found.', 'error')
        return redirect('/my_books')

    flash('Payment successful. You can now download the book.', 'success')
    return redirect('/my_books')

@app.route('/return', methods=['POST'])
def return_book():
    book_id = request.form['id']
    user_id = session.get('user_id')
    bookissued = BookIssued.query.filter_by(book_id=book_id, user_id=user_id).first()

    if bookissued:  
        book = Book.query.get(book_id)
        book.Quantity += 1  
        db.session.delete(bookissued)  
        db.session.commit()

        flash('Book is returned successfully')
    else:
        flash('Return failed', 'error')

    return redirect('/my_books')


@app.route('/rate_book/<int:book_id>', methods=['GET', 'POST'])
def rate_book(book_id):
    book = Book.query.get(book_id)
    user_id= session.get('user_id')
    ratingandfeedbacks=RatingFeedback.query.all()
    if not book:
        flash('Book not found.', 'error')
        return redirect('/my_books')

    if request.method == 'POST':
        rating = request.form['rating']
        feedback = request.form['feedback']
        new_rf = RatingFeedback(book_id=book_id, user_id=user_id, rating=rating, feedback=feedback)
        try:
            db.session.add(new_rf)
            db.session.commit()
            flash('Thank you for your rating and feedback!', 'success')
            return redirect(f'/rate_book/{book_id}')
        except IntegrityError:
            db.session.rollback()
            flash('Unable to rate/feedback','error')
            return redirect('/udash')

    return render_template('rate_book.html', book=book,ratingandfeedbacks=ratingandfeedbacks)
# -- End of User dashboard --

#book management code
@app.route('/issuetou', methods=['GET','POST'])
def issuetou():
    booksall=Book.query.all()
    books=BookIssued.query.all()
    users=User.query.all()
    if request.method=='POST':
        book_id = request.form['book']  
        book = Book.query.get(book_id)
        user_id = request.form['user']  
        if book.Quantity > 0 :
            book.Quantity -= 1
            new_issue = BookIssued(user_id=user_id, book_id=book_id, issue_date = datetime.utcnow(), return_date = datetime.utcnow() + timedelta(days=7))
            db.session.add(new_issue)
            flash('Book is successfully issued')
            db.session.commit()
        else:
            flash('The book is issued by other user','error')
        
        
    return render_template('issuetou.html',books=books, users=users,booksall=booksall)   
@app.route('/revoke', methods=['POST'])
def revoke_access():
    book_id = request.form['title']
    booki = BookIssued.query.filter_by(book_id=book_id).first()
    user_id=request.form['user_id']
    user=User.query.filter_by(id=user_id).first()
    if booki.user_id == user.id:
        book=Book.query.get(book_id)
        book.Quantity +=1
        db.session.delete(booki)
        db.session.commit()
        flash('Access to the book has been revoked successfully.', 'success')
    else:
        flash('Access to the book cannot be revoked for this user.', 'error')
    return redirect('/issuetou') 

@app.route('/editbook/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get(book_id)
    sections = Section.query.all()
    if not book:
        flash('Book not found.', 'error')
        return redirect('/admindashboard')

    if request.method == 'POST':
        
        title = request.form['title'].strip() 
        author = request.form['author'].strip()
        quantity = request.form['quantity'].strip()
        pdf_path = request.form['pdf_path'].strip()
        content = request.form['Content'].strip()
        section_id = request.form['section'].strip()
        print(quantity)
        if title:
            book.title = title
        if author:
            book.author = author
        
        if pdf_path:
            book.pdf_path = pdf_path
        if content:
            book.content = content
        if section_id:
            if section_id == 'Unassigned':
                book.section_id=0
            else:
                book.section_id=section_id
        if quantity:
            print(quantity)
            new_quantity = int(quantity)
            if new_quantity >= 0:  
                book.Quantity = new_quantity
                print(book.Quantity)
        db.session.commit()
        flash('Book details updated successfully.', 'success')
        return redirect(f'/editbook/{book_id}')
    return render_template('editbook.html', book=book, sections=sections)
@app.route('/add_book', methods=['GET','POST'])
def add_book_to_section():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        section_id = request.form['section']  
        section = Section.query.get(section_id)
        Content= request.form['content']
        Quantity=request.form['quantity']
        pdf_path=request.form['pdf_path']
        
        if not section:
            flash('Section does not exist.', 'error')
            return redirect('/add_book')
        new_book = Book(title=title, author=author, section_id=section_id,Content=Content,pdf_path=pdf_path,Quantity=Quantity)

        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect("/add_book")
    sections = Section.query.all()
    return render_template('add_book.html', sections=sections)
@app.route('/remove_book', methods=['GET', 'POST'])
def remove_book():
    if request.method == 'POST':
        book_id = request.form['book']
        book = Book.query.get(book_id)

        try:
            if request.form['answer']=='yes':
                db.session.delete(book)
                db.session.commit()
                return redirect('/admindashboard')
            else:
                return redirect('/admindashboard')

        except IntegrityError:
            db.session.rollback()
            return 'Error removing the section. Please try again.'
    books = Book.query.all()
    return render_template('remove_book.html', books=books)
# Section management code
@app.route('/editsection/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    section = Section.query.get(section_id)
    if not section:
        flash('section not found.', 'error')
        return redirect('/admindashboard')

    if request.method == 'POST':
        name = request.form['name'].strip() 
        description = request.form['description'].strip()

        if name:
            section.name = name
        if description:
            section.description = description
        db.session.commit()
        flash('Section details updated successfully.', 'success')
        return redirect(f'/editsection/{section_id}')
    return render_template('editsection.html', section=section)
@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        name = request.form['name']
        description= request.form['Description']

        new_section = Section(name=name, description=description)

        try:
            db.session.add(new_section)
            db.session.commit()
            return redirect('/admindashboard')
        except IntegrityError:
            db.session.rollback()
            return 'Error adding the section. Please try again.'

    return render_template('add_section.html')
@app.route('/remove_section', methods=['GET', 'POST'])
def remove_section():
    if request.method == 'POST':
        section_id = request.form['section']
        section = Section.query.get(section_id)
        books=Book.query.filter_by(section_id=section_id)

        try:
            if request.form['answer']=='yes':
                for book in books:
                    book.section_id=0
                db.session.commit()
                db.session.delete(section)
                db.session.commit()
                return redirect('/admindashboard')
            else:
                return redirect('/admindashboard')

        except IntegrityError:
            db.session.rollback()
            return 'Error removing the section. Please try again.'

    sections = Section.query.all()
    return render_template('remove_section.html', sections=sections)
# profile of librarian
@app.route('/profile')
def profile():
    admin=Admin.query.get(session['admin_id'])
    return render_template('adprofile.html',admin_username=admin.username, admin_password=admin.password)

@app.route('/changepass', methods=['POST'])
def changepass():
    admin=Admin.query.get(session['admin_id'])
    admin_password=request.form['admin_password']
    admin.password = admin_password
    db.session.commit()
    return redirect('/profile')
   
@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect('/home')
@app.route('/admindashboard')
def admin_dashboard():
    admin = Admin.query.get(session['admin_id'])

    books = Book.query.all()
    sections = Section.query.all()
    users = User.query.all()
    book_requests = BookRequest.query.all()

    return render_template('dashboard.html', admin_username=admin.username,
                           books=books, sections=sections, users=users, book_requests=book_requests)
# user management code
@app.route('/changeDes', methods=['GET','POST'])
def changedes():
    users = User.query.all()
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        
        if user:
            new_admin = Admin(username=user.username, password=user.password)
            try:
                db.session.add(new_admin)
                db.session.commit()
                flash('The Designation is successfully changed')
                return redirect('/changeDes')
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred while adding the user as admin.', 'error')
                return redirect('/changeDes')
        else:
            flash('User not found.', 'error')
            return redirect('/changeDes')
    
    return render_template('changeDes.html', users=users)
@app.route('/add_user',methods=['GET','POST'])
def add_user():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User is successfully added')
            return redirect('/add_user')
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already exists. Please choose a different one.','error')
            return redirect('/add_user')
    
    return render_template('add_user.html')
@app.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    if request.method == 'POST':
        user_id = request.form['user']
        user = User.query.get(user_id)

        try:
            if request.form['answer']=='yes':
                db.session.delete(user)
                db.session.commit()
                return redirect('/admindashboard')
            else:
                return redirect('/admindashboard')

        except IntegrityError:
            db.session.rollback()
            flash('Error removing the section. Please try again.','error')
    users = User.query.all()
    return render_template('remove_user.html', users=users)
#login system of librarian
@app.route('/adminlogin',methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST':
        admin_username = request.form['username']
        admin_password = request.form['password']

        admin = Admin.query.filter_by(username=admin_username, password=admin_password).first()

        if admin:
            session['admin_id'] = admin.id
            return redirect('/admindashboard')
        else:
            flash('Invalid username or password. Please try again.', 'error')
           
    return render_template('adminlogin.html')

#accept/reject/cancel book request code 
@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    req = BookRequest.query.get(request_id)
    if not req:
        flash('Request not found.', 'error')
        return redirect('/admindashboard')

    if req.status != 'pending':
        flash('Request has already been processed.', 'error')
        return redirect('/admindashboard')

    req.status = 'rejected'
    db.session.delete(req)
    db.session.commit()

    flash('Book request has been rejected.', 'success')
    return redirect('/admindashboard')
@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    request_to_accept = BookRequest.query.get(request_id)
    if request_to_accept:
        book_id = request_to_accept.book_id
        user_id = request_to_accept.user_id
        book = Book.query.get(book_id)
        bookissue=BookIssued.query.filter_by(book_id=book_id,user_id=user_id).first()
        if bookissue:
            db.session.delete(request_to_accept)
            db.session.commit()
            flash("The book is already been issued. The request have been deleted",'error')
        else:
            if book and book.Quantity > 0:
                book.Quantity -= 1
                new_issue = BookIssued(user_id=user_id, book_id=book_id, issue_date = datetime.utcnow(), return_date = datetime.utcnow() + timedelta(days=7))
                db.session.delete(request_to_accept)
                db.session.commit()
                db.session.add(new_issue)
                db.session.commit()
                flash('Book request accepted successfully!', 'success')
            else:
                flash('Unable to accept book request. Either the book is unavailable or the request is invalid.', 'error')

    return redirect('/admindashboard')

@app.route('/cancel_request/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    req = BookRequest.query.get(request_id)
    db.session.delete(req)
    db.session.commit()
    flash('Book request has been canceled.', 'success')
    return redirect('/uprofile')
# the below code is to check if there anre any overdue books or not
def check_overdue_books():
    now = datetime.now()
    overdue_books = BookIssued.query.filter(BookIssued.return_date < now).all()
    for book in overdue_books:
            book_id=book.book_id
            b=Book.query.get(book_id)
            b.Quantity += 1
            db.session.delete(book)
            db.session.commit()

    flash(f'Book "{b.title}" has been automatically returned due to overdue.', 'warning')

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        check_overdue_books()
    app.run(debug=True)