from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from models import Admin, Opportunity, db


bp = Blueprint("main", __name__)


def _json_body():
    return request.get_json(silent=True) or request.form.to_dict() or {}


def _normalize_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _validate_email(email):
    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError:
        return None


def _token_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _extract_opportunity_payload(data):
    required = [
        "name",
        "duration",
        "start_date",
        "description",
        "skills",
        "category",
        "max_applicants",
    ]

    errors = []
    for field in required:
        if not str(data.get(field, "")).strip():
            errors.append(f"{field} is required")

    category = str(data.get("category", "")).strip()
    if category and category not in current_app.config["ALLOWED_CATEGORIES"]:
        errors.append("category is invalid")

    max_applicants = data.get("max_applicants")
    try:
        max_applicants = int(max_applicants)
        if max_applicants <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("max_applicants must be a positive integer")

    if errors:
        return None, errors

    payload = {
        "name": str(data.get("name")).strip(),
        "duration": str(data.get("duration")).strip(),
        "start_date": str(data.get("start_date")).strip(),
        "description": str(data.get("description")).strip(),
        "skills": str(data.get("skills")).strip(),
        "category": category,
        "future_opportunities": _normalize_bool(data.get("future_opportunities")),
        "max_applicants": max_applicants,
    }
    return payload, None


@bp.get("/")
def index_page():
    return render_template("index.html")


@bp.get("/login")
def login_page():
    return render_template("login.html")


@bp.get("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", user=current_user)


@bp.get("/reset-password/<token>")
def reset_password_page(token):
    return render_template("reset_password.html", token=token)


@bp.post("/api/signup")
def signup():
    data = _json_body()
    full_name = str(data.get("full_name", "")).strip()
    email_raw = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))
    confirm_password = str(data.get("confirm_password", ""))

    if not full_name or not email_raw or not password or not confirm_password:
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    email = _validate_email(email_raw)
    if not email:
        return jsonify({"status": "error", "message": "Invalid email format"}), 400

    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    if len(password) < 8:
        return jsonify({"status": "error", "message": "Password must be at least 8 characters"}), 400

    if Admin.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already registered"}), 409

    admin = Admin(
        full_name=full_name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(admin)
    db.session.commit()

    return jsonify({"status": "success", "message": "Signup successful"}), 201


@bp.post("/api/login")
def login():
    data = _json_body()
    email_raw = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))
    remember = _normalize_bool(data.get("remember"))

    email = _validate_email(email_raw)
    if not email or not password:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    user = Admin.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

    login_user(user, remember=remember)
    if remember:
        current_app.permanent_session_lifetime = current_app.config["REMEMBER_COOKIE_DURATION"]

    return jsonify({"status": "success", "message": "Login successful", "user": user.to_dict()}), 200


@bp.post("/api/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status": "success", "message": "Logged out"}), 200


@bp.post("/api/forgot-password")
def forgot_password():
    data = _json_body()
    email_raw = str(data.get("email", "")).strip()
    email = _validate_email(email_raw)
    reset_link = None

    if email:
        user = Admin.query.filter_by(email=email).first()
        if user:
            token = _token_serializer().dumps(user.email, salt="reset-password")
            reset_link = request.host_url.rstrip("/") + f"/reset-password/{token}"
            print(f"[Password Reset] {user.email}: {reset_link}")

    response = {"status": "success", "message": "If that email exists, reset instructions have been generated."}
    if reset_link:
        response["reset_link"] = reset_link

    return jsonify(response), 200


@bp.post("/api/reset-password/<token>")
def reset_password(token):
    data = _json_body()
    password = str(data.get("password", ""))
    confirm_password = str(data.get("confirm_password", ""))

    if len(password) < 8:
        return jsonify({"status": "error", "message": "Password must be at least 8 characters"}), 400

    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    try:
        email = _token_serializer().loads(
            token,
            salt="reset-password",
            max_age=current_app.config["RESET_TOKEN_MAX_AGE_SECONDS"],
        )
    except SignatureExpired:
        return jsonify({"status": "error", "message": "Reset token has expired"}), 400
    except BadSignature:
        return jsonify({"status": "error", "message": "Invalid reset token"}), 400

    user = Admin.query.filter_by(email=email).first()
    if not user:
        return jsonify({"status": "error", "message": "Invalid reset token"}), 400

    user.password_hash = generate_password_hash(password)
    db.session.commit()

    return jsonify({"status": "success", "message": "Password reset successful"}), 200


@bp.get("/api/opportunities")
@login_required
def list_opportunities():
    rows = Opportunity.query.filter_by(admin_id=current_user.id).order_by(Opportunity.id.desc()).all()
    return jsonify({"status": "success", "data": [row.to_dict() for row in rows]}), 200


@bp.post("/api/opportunities")
@login_required
def create_opportunity():
    data = _json_body()
    payload, errors = _extract_opportunity_payload(data)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    row = Opportunity(**payload, admin_id=current_user.id)
    db.session.add(row)
    db.session.commit()
    return jsonify({"status": "success", "data": row.to_dict()}), 201


@bp.get("/api/opportunities/<int:opportunity_id>")
@login_required
def get_opportunity(opportunity_id):
    row = Opportunity.query.filter_by(id=opportunity_id, admin_id=current_user.id).first()
    if not row:
        return jsonify({"status": "error", "message": "Opportunity not found"}), 404
    return jsonify({"status": "success", "data": row.to_dict()}), 200


@bp.put("/api/opportunities/<int:opportunity_id>")
@login_required
def update_opportunity(opportunity_id):
    row = Opportunity.query.filter_by(id=opportunity_id, admin_id=current_user.id).first()
    if not row:
        return jsonify({"status": "error", "message": "Opportunity not found"}), 404

    data = _json_body()
    payload, errors = _extract_opportunity_payload(data)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    for key, value in payload.items():
        setattr(row, key, value)

    db.session.commit()
    return jsonify({"status": "success", "data": row.to_dict()}), 200


@bp.delete("/api/opportunities/<int:opportunity_id>")
@login_required
def delete_opportunity(opportunity_id):
    row = Opportunity.query.filter_by(id=opportunity_id, admin_id=current_user.id).first()
    if not row:
        return jsonify({"status": "error", "message": "Opportunity not found"}), 404

    db.session.delete(row)
    db.session.commit()
    return jsonify({"status": "success", "message": "Opportunity deleted"}), 200
