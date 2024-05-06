# Library Management System
This is a Library Management System built using Flask, SQLAlchemy, HTML,CSS and SQLite. The system allows users to register, log in, search for books, request books, view their profile, issue and return books, rate and provide feedback on books, and administrators can manage books, sections, users, and book requests.
## Features
* **User Management:** Users can register, log in, and change passwords.
* **Book Management:** Administrators can add, edit, and remove books, and assign them to sections. Users can search for books, request books, and view their issued books.
* **Section Management:** Administrators can add, edit, and remove sections.
* **Request Management:** Administrators can accept, reject, and cancel book requests.
* **Rating and Feedback:** Users can rate and provide feedback on books.
* **PDF Viewer:** View PDFs of books directly in the browser.
## Requirements
* Python 3.x
* Flask
* Flask-SQLAlchemy
* SQLite
## Setup
1. Clone the repository:
```
git clone https://github.com/Deepcoder2905/library-management-system.git
```
2. Install dependencies:
```
pip install -r requirements
```
   requirements are all the neccessary libraries that are required for the app
3. Run the application:
 ```
python app.py
```
4. Access the application in your web browser at http://localhost:5000.

## Project Structure
* **static/:** Contains static files such as images and PDFs.
* **templates/:** Contains HTML templates.
* **Instance/:** Contains the database.
* **app.py:** Main application file. (This include the main code along with the models)
* **README.md:** This file.
* **Project Documentation:** This stores the detail information about the project.

## Usage
* Upon running the application, users can register and log in.
* Users can search for books, request books, view their profile, and issue or return books.
* Administrators can log in to manage books, sections, users, and book requests from the admin dashboard.

## Contributions
Contributions are welcome! If you have any suggestions or found a bug, feel free to open an issue or create a pull request.
