# Qatar Foundation Admin Portal - Submission README

## 1. Project Overview
This project is a full-stack Flask Admin Portal with secure authentication and opportunity management.

Implemented modules:
- Admin Sign Up, Login, Logout
- Forgot Password (token link logged in console)
- Opportunity CRUD (Create, Read, Update, Delete)
- Session-based access control with Flask-Login
- Admin-only ownership checks for opportunities

## 2. Tech Stack
- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- PostgreSQL (primary) / SQLite (fallback)
- HTML, CSS, Vanilla JavaScript

## 3. Project Structure
```text
qatar_foundation_admin/
├── app.py
├── config.py
├── models.py
├── routes.py
├── requirements.txt
├── .env
├── static/
│   ├── css/styles.css
│   └── js/
│       ├── auth.js
│       └── dashboard.js
└── templates/
    ├── index.html
    ├── login.html
    └── dashboard.html
```

## 4. Setup Instructions
1. Open terminal in project directory.
2. Create and activate virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```
3. Install dependencies:
```powershell
pip install -r requirements.txt
```
4. Configure environment variables in `.env`:
```env
SECRET_KEY=dev-secret-change-me
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
DB_NAME=qf_admin
```
5. Run application:
```powershell
python app.py
```
6. Open:
- http://127.0.0.1:5000/

## 5. API Endpoints
### Auth
- `POST /api/signup`
- `POST /api/login`
- `POST /api/logout`
- `POST /api/forgot-password`
- `POST /api/reset-password/<token>`

### Opportunities
- `GET /api/opportunities`
- `POST /api/opportunities`
- `GET /api/opportunities/<id>`
- `PUT /api/opportunities/<id>`
- `DELETE /api/opportunities/<id>`

## 6. Security Features
- Password hashing using Werkzeug (`generate_password_hash`, `check_password_hash`)
- Generic login error message: "Invalid email or password"
- Forgot-password response does not reveal whether email exists
- Login-required protection for opportunity routes
- Opportunity ownership enforced via `admin_id == current_user.id`

## 7. Demo Flow (For Evaluation)
1. Open landing page.
2. Click **Sign Up**, create admin account.
3. Click **Login**, sign in.
4. In dashboard, add a new opportunity.
5. Verify list updates without page refresh.
6. Edit opportunity and save.
7. Delete opportunity.
8. Test forgot password request and check console reset link.

## 8. Notes
- PostgreSQL database is auto-created at startup if missing (with sufficient DB user privileges).
- UI structure remains aligned with assignment flow; backend routes return JSON for dynamic updates.
