import json
from openai import OpenAI
from config import Config
from datetime import datetime, timedelta

client = OpenAI(api_key=Config.OPENAI_API_KEY)


def get_meal_plan(data: dict) -> dict:
    today = datetime.now().date()

    answer_in_json = """{
    "{Дата в формате YYYY-MM-DD (начиная с понедельника и заканчивая воскресеньем этой недели)}": {
    "{Название приема пищи (Завтрак, Обед, Ужин, Перекус)}-{время приема пищи}": [
        # Список продуктов
        { name: {Название продукта}, calories: <int>, fats: <int>, proteins: <int>, carbs: <int> }
    ]
    }"""

    prompt = f"""
    Создай план питания на неделю, основываясь на следующих параметрах:
    Возраст: {data["age"]}, Вес: {data["weight"]}, 
    Телосложение: {data["body_type"]}, Пол: {data["gender"]}, 
    Цель питания: {data["nutrition_purpose"]},
    Аллергии: {data["allergies"]}, Предпочтения в еде: {data["food_preferences"]}, 
    Образ жизни: {data["lifestyle"]}, 
    Диетические ограничения: {data["dietary_restrictions"]}, 
    Сон: {data["sleep"]}, Доступные продукты: {data["available_products"]}, 
    Пожелания: {data["wishes"]}.

    Формат ответа в виде json: {answer_in_json}
    ВАЖНО: Формат ответа должен 100% соответствовать описанию выше, без лишних слов, 
    только план питания и обязательно на все 7 дней — 
    с текущего понедельника ({today - timedelta(days=today.weekday())}) 
    по воскресенье ({today + timedelta(days=6 - today.weekday())}).
    """

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Ты — помощник по питанию, возвращай только JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    output = response.choices[0].message.content
    if output.startswith("```json"):
        output = output.replace("```json", "")
        output = output.replace("```", "")

    # print(output, end="\n\n\n")
    return json.loads(output)


# data = {
#     "age": 25,
#     "weight": 70,
#     "body_type": "мезоморф",
#     "gender": "мужской",
#     "nutrition_purpose": "набор массы",
#     "allergies": "арахис",
#     "food_preferences": "мясо, молочные продукты, крупы",
#     "lifestyle": "активный (тренировки 4 раза в неделю)",
#     "dietary_restrictions": "без глютена",
#     "sleep": "7-8 часов",
#     "available_products": "курица, говядина, рис, гречка, яйца, творог, яблоки, бананы, брокколи, морковь, картофель",
#     "wishes": "вкусный и разнообразный рацион"
# }
# print(get_meal_plan(data))
