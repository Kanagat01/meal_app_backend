from flask import Blueprint, jsonify
from flask_pydantic import validate
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from schemas import *
from models import UserProfile, db, User, Token

auth_bp = Blueprint('auth', __name__, url_prefix='/auth/')


@auth_bp.route('register/', methods=['POST'])
@validate()
def register(body: UserCreateSchema):
    data = body.model_dump()
    password = data.pop("password")

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Такой логин уже существует"}), 400

    user = User(**data)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    db.session.add(
        Token(user_id=user.id, jti=access_token, token_type='access'))
    db.session.add(
        Token(user_id=user.id, jti=refresh_token, token_type='refresh'))
    db.session.commit()

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route('login/', methods=['POST'])
@validate()
def login(body: UserLoginSchema):
    user: User = User.query.filter(
        User.username == body.username
    ).first()

    if not user or not user.check_password(body.password):
        return jsonify({"error": "Неправильный логин или пароль"}), 400

    tokens = Token.query.filter_by(user_id=user.id)
    for token in tokens:
        token.revoked = True
        db.session.add(token)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    db.session.add(
        Token(user_id=user.id, jti=access_token, token_type='access'))
    db.session.add(
        Token(user_id=user.id, jti=refresh_token, token_type='refresh'))
    db.session.commit()

    does_profile_exist = bool(
        UserProfile.query.filter_by(user_id=user.id).first())

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "does_profile_exist": does_profile_exist,
    }), 200


@auth_bp.route('refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=str(current_user))
    return jsonify({"access_token": new_access_token}), 200


# @auth_bp.route('/logout', methods=['GET'])
# @jwt_required()
# def logout():
#     user_id = get_jwt_identity()
#     tokens = Token.query.filter_by(user_id=user_id)
#     for token in tokens:
#         token.revoked = True
#         db.session.add(token)
#     db.session.commit()
#     return jsonify({"message": "Вы успешно вышли из аккаунта"}), 200
