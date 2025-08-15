from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from datetime import date, datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLD_LOGIN = "12admin34"
OLD_PASSWORD = "pAss_12uH11"
OLD_DATE = date(1997, 4, 13)


class UpdateRequest(BaseModel):
    login: str
    password: str
    date: str

    @validator('login')
    def validate_login(cls, v):
        if v == "":
            return v
        import re
        if len(v) > 10:
            raise ValueError("Логин должен быть максимум 10 символов")
        if not re.fullmatch(r'[A-Za-z0-9_]+', v):
            raise ValueError("Логин может содержать только латиницу, цифры и нижнее подчёркивание")
        return v

    @validator('password')
    def validate_password(cls, v):
        if v == "":
            return v
        if len(v) < 8 or len(v) > 16:
            raise ValueError("Пароль должен быть от 8 до 16 символов")
        for ch in v:
            if ord(ch) < 32 or ord(ch) > 126:
                raise ValueError("Пароль должен содержать только ASCII символы без пробелов")
        return v

    @validator('date')
    def validate_date(cls, v):
        if v == "":
            return v
        try:
            d = datetime.strptime(v, "%Y-%m-%d").date()
        except Exception:
            raise ValueError("Неверный формат даты")
        today = date.today()
        if d > today:
            raise ValueError("Дата рождения не может быть позже сегодняшней")
        age = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
        if age < 18:
            raise ValueError("Пользователь должен быть совершеннолетним")
        if age > 100:
            raise ValueError("Пользователь не может быть старше 99 лет")
        return v


@app.get("/")
def get_old_data():
    return {
        "login": OLD_LOGIN,
        "password": OLD_PASSWORD,
        "date": OLD_DATE.isoformat()
    }


@app.post("/update")
def update_data(data: UpdateRequest):
    errors = {}

    # Проверяем каждое поле на совпадение со старым
    if data.login == OLD_LOGIN:
        errors["login"] = "Такой логин уже используется"
    if data.password == OLD_PASSWORD:
        errors["password"] = "Такой пароль уже используется"
    if data.date == OLD_DATE.isoformat():
        errors["date"] = "Такая дата уже установлена"

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    # Формируем результат: если пустая строка — оставляем старое значение
    result = {
        "login": data.login if data.login != "" else OLD_LOGIN,
        "password": data.password if data.password != "" else OLD_PASSWORD,
        "date": data.date if data.date != "" else OLD_DATE.isoformat()
    }

    return result