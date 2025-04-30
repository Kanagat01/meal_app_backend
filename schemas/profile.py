from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class UserSchema(BaseModel):
    id: int
    full_name: str
    username: str

    class Config:
        from_attributes = True


class BodyTypeEnum(str, Enum):
    ECTOMORPH = "Эктоморф"
    MESOMORPH = "Мезоморф"
    ENDOMORPH = "Эндоморф"


class GenderEnum(str, Enum):
    MALE = "Мужской"
    FEMALE = "Женский"


class NutritionGoalEnum(str, Enum):
    LOSE_WEIGHT = "Потеря веса"
    GAIN_WEIGHT = "Набор веса"
    MEDICAL = "Лечебное"


class LifestyleEnum(str, Enum):
    SEDENTARY = "Малоактивный"
    LOW_ACTIVE = "1-2 тренировки в неделю"
    ACTIVE = "3-4 тренировки в неделю"
    VERY_ACTIVE = "5-7 тренировок в неделю"


class SleepEnum(str, Enum):
    SHORT = "4-5 часа"
    NORMAL = "5-7 часа"
    LONG = "8-10 часа"


class UserProfileSchema(BaseModel):
    age: int = Field(..., ge=1, le=120,
                     description="Возраст должен быть от 1 до 120 лет")
    weight: float = Field(..., ge=20.0, le=300.0,
                          description="Вес должен быть от 20 до 300 кг")

    body_type: BodyTypeEnum
    gender: GenderEnum
    nutrition_purpose: NutritionGoalEnum

    lifestyle: Optional[LifestyleEnum] = None
    sleep: Optional[SleepEnum] = None
    allergies: Optional[str] = None
    food_preferences: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    available_products: Optional[str] = None
    wishes: Optional[str] = None

    class Config:
        extra = 'forbid'
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            Enum: lambda e: e.value
        }

    @field_validator('age')
    def validate_age(cls, value):
        if value < 1 or value > 120:
            raise ValueError("Возраст должен быть от 1 до 120 лет")
        return value

    @field_validator('weight')
    def validate_weight(cls, value):
        if value < 20 or value > 300:
            raise ValueError("Вес должен быть от 20 до 300 кг")
        return value
