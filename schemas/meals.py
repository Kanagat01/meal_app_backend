from datetime import date as Date, time as Time
from pydantic import BaseModel, computed_field, field_serializer


class ProductSchema(BaseModel):
    id: int
    name: str
    calories: int
    proteins: int
    fats: int
    carbs: int
    completed: bool

    class Config:
        from_attributes = True


class MealSchema(BaseModel):
    id: int
    meal_type: str
    date: Date
    time: Time
    products: list[ProductSchema]

    class Config:
        from_attributes = True

    @field_serializer("date", mode="plain")
    def _ser_date(self, v: Date, info):
        # 'YYYY-MM-DD'
        return v.isoformat()

    @field_serializer("time", mode="plain")
    def _ser_time(self, v: Time, info):
        # 'HH:mm'
        return v.strftime("%H:%M")

    @computed_field
    @property
    def total_nutrients(self) -> dict[str, int]:
        nutrients = {'calories': 0, 'proteins': 0, 'fats': 0, 'carbs': 0}
        for product in self.products:
            nutrients['calories'] += product.calories
            nutrients['proteins'] += product.proteins
            nutrients['fats'] += product.fats
            nutrients['carbs'] += product.carbs
        return nutrients
