from datetime import datetime, time
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.sql import expression
from openai_client import get_meal_plan

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    jti = db.Column(db.String(36), unique=True, nullable=False)
    token_type = db.Column(db.String(10))  # access/refresh
    revoked = db.Column(db.Boolean, default=False)


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    body_type = db.Column(db.Enum('Эктоморф', 'Мезоморф',
                          'Эндоморф', name='body_types'), nullable=False)
    gender = db.Column(db.Enum('Мужской', 'Женский',
                       name='genders'), nullable=False)
    nutrition_purpose = db.Column(db.Enum(
        'Потеря веса', 'Набор веса', 'Лечебное', name='nutrition_purposes'), nullable=False)
    allergies = db.Column(db.String(200), nullable=True)
    food_preferences = db.Column(db.String(200), nullable=True)
    lifestyle = db.Column(db.Enum('Малоактивный', '1-2 тренировки в неделю',
                          '3-4 тренировки в неделю', '5-7 тренировок в неделю', name='lifestyles'), nullable=True)
    dietary_restrictions = db.Column(db.String(200), nullable=True)
    sleep = db.Column(db.Enum('4-5 часа', '5-7 часа',
                      '8-10 часа', name='sleeps'), nullable=True)
    available_products = db.Column(db.String(300), nullable=True)
    wishes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meal_type = db.Column(db.Enum('Завтрак', 'Обед', 'Ужин',
                          'Перекус', name='meal_types'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    products = db.relationship('Product', backref='meal', lazy=True)
    completed = db.Column(db.Boolean, default=False,
                          server_default=expression.false())

    @property
    def total_nutrients(self):
        nutrients = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
        for product in self.products:
            nutrients['calories'] += product.calories
            nutrients['proteins'] += product.proteins
            nutrients['fats'] += product.fats
            nutrients['carbs'] += product.carbs
        return nutrients

    @classmethod
    def create_new_plan(cls, user_id: int, data: dict):
        meals_data = get_meal_plan(data)
        created_meals = []
        for date, meals in meals_data.items():
            for key, products_data in meals.items():
                products = [Product(**p) for p in products_data]
                meal_type, meal_time = key.split("-")
                hour, minute = map(int, meal_time.split(":"))
                meal = Meal(
                    user_id=user_id,
                    meal_type=meal_type,
                    date=datetime.strptime(date, '%Y-%m-%d'),
                    time=time(hour, minute),
                    products=products
                )
                db.session.add(meal)
                created_meals.append(meal)
        try:
            db.session.commit()
            return created_meals
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f'<{self.date} {self.meal_type} {self.time}>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey(
        'meal.id', name='fk_product_meal_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    proteins = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'
