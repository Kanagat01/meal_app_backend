import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app, url_for
from flask_pydantic import validate
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from models import db, Meal, UserProfile, User
from schemas import *

profile_bp = Blueprint('profile', __name__, url_prefix='/user/')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB


@profile_bp.route('upload_photo/', methods=['POST'])
@jwt_required()
def upload_user_photo():
    """Эндпоинт для обновления фотографии пользователя"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if 'file' not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Файл не выбран"}), 400

    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
        return jsonify({"error": "Недопустимый формат файла. Список доступных разрешений: png, jpg, jpeg, gif"}), 400

    try:
        filename = secure_filename(file.filename)
        unique_filename = f"{user_id}_{filename}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        user.photo_url = unique_filename
        db.session.commit()

        return jsonify({
            "photo_url": url_for('profile.get_photo', filename=unique_filename, _external=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@profile_bp.route('photos/<filename>/')
def get_photo(filename):
    """Эндпоинт для получения фотографии"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@profile_bp.route('get_user_data/', methods=['GET'])
@jwt_required()
def get_user_data():
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id).first()
    profile = UserProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({"error": "Профиль не найден"}), 404
    return jsonify({
        'user': {
            **UserSchema.model_validate(user).model_dump(),
            'photo_url': url_for('profile.get_photo', filename=user.photo_url, _external=True) if user.photo_url else None
        },
        'profile': UserProfileSchema.model_validate(profile).model_dump()
    }), 200


@profile_bp.route('set_user_profile/', methods=['POST'])
@jwt_required()
@validate()
def set_user_profile(body: UserProfileSchema):
    current_user_id = get_jwt_identity()
    try:
        data = body.model_dump()
    except ValidationError as err:
        return jsonify({"error": err.errors()}), 400

    existing_profile = UserProfile.query.filter_by(
        user_id=current_user_id).first()
    if existing_profile:
        for key, value in data.items():
            setattr(existing_profile, key, value)
    else:
        profile = UserProfile(user_id=current_user_id, **data)
        db.session.add(profile)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

    if not existing_profile:
        try:
            Meal.create_new_plan(current_user_id, data)
        except Exception as e:
            return jsonify({"error": f"Произошла ошибка при создании плана питания: {str(e)}"}), 400

    response = UserProfileSchema.model_validate(
        existing_profile if existing_profile else profile)
    return jsonify({"profile": response.model_dump()}), 200 if existing_profile else 201
