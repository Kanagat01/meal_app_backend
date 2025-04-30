from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from schemas import *
from models import *

meals_bp = Blueprint('meals', __name__, url_prefix='/meals/')


@meals_bp.route('get_meals/', methods=['GET'])
@jwt_required()
def get_meals():
    user_id = get_jwt_identity()
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)

        meals = Meal.query.filter(
            Meal.user_id == user_id,
            Meal.date >= start_date,
            Meal.date <= end_date
        ).order_by(Meal.date, Meal.time).all()

        if len(meals) == 0 and not start_date_str:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            data = UserProfileSchema.model_validate(profile).model_dump()

            try:
                meals = Meal.create_new_plan(user_id, data)
            except Exception as e:
                return jsonify({"error": f"Произошла ошибка при создании плана питания: {str(e)}"}), 400

        meals_data = [MealSchema.model_validate(
            meal).model_dump() for meal in meals]
        return jsonify({'meals': meals_data})

    except ValueError as e:
        return jsonify({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@meals_bp.route('change_product_status/', methods=['GET'])
@jwt_required()
def change_product_status():
    user_id = get_jwt_identity()
    product = Product.query.join(Meal).filter(
        Product.id == request.args.get('product_id'),
        Meal.user_id == user_id
    ).first()
    if not product:
        return jsonify({'error': 'Продукт не найден'}), 404

    product.completed = not product.completed
    db.session.commit()
    return jsonify({'message': 'Статус продукта изменен'}), 200
