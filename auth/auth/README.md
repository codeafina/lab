# Python Authentication – CI/CD Project

## 📌 Project Description
This project presents an implementation of a simple authentication module
written in Python using the Flask framework.  
The main goal of the project is to demonstrate the design and implementation
of a CI/CD pipeline with automated testing.

## 🎯 Project Scope
The project focuses exclusively on:
- user authentication
- session handling
- protection against brute-force attacks
- automated testing and CI pipeline

Other application functionalities are intentionally excluded.

## 🧱 Technologies Used
- Python 3
- Flask
- Werkzeug
- Pytest
- GitHub Actions (CI/CD)

## 🚀 Running the Application

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt
python app.py
```

## Application will be available at:

```bash
Running on http://127.0.0.1:5000
```

## 🧪 Running Tests

```bash
pytest -v
```

## 🔄 CI/CD Pipeline

The CI/CD pipeline is implemented using GitHub Actions.
It automatically:

installs dependencies

runs unit tests

validates authentication logic on every push and pull request

## 📂 Project Structure

```bash
auth/        - authentication logic
tests/       - unit tests
templates/   - HTML templates
static/      - CSS styles
.github/     - CI configuration
```

## 👤 Author

Alina Sukash