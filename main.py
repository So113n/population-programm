import sqlite3
from enum import Enum
from dataclasses import dataclass
from typing import List

# -----------------------------
# ENUMS & DATA MODEL
# -----------------------------

class Gender(str, Enum):
    MALE = 'м'
    FEMALE = 'ж'

class Education(str, Enum):
    PRIMARY = 'н'      # начальное
    SECONDARY = 'с'    # среднее
    HIGHER = 'в'       # высшее

@dataclass
class Form:
    age: int
    gender: Gender
    education: Education
    answer_yes: bool

# -----------------------------
# DATABASE LAYER
# -----------------------------

DB_FILE = 'DataBase.db'
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS forms (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    age         INTEGER NOT NULL CHECK(age BETWEEN 0 AND 120),
    gender      TEXT    NOT NULL CHECK(gender IN ('м','ж')),
    education   TEXT    NOT NULL CHECK(education IN ('н','с','в')),
    answer_yes  INTEGER NOT NULL CHECK(answer_yes IN (0,1))
);
"""

def open_db(path: str = DB_FILE) -> sqlite3.Connection:
    """Open connection and ensure schema exists."""
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA_SQL)
    conn.commit()
    return conn

def read_int(prompt: str, lo: int, hi: int) -> int:
    while True:
        try:
            val = int(input(prompt))
            if lo <= val <= hi:
                return val
            print(f'Введите число от {lo} до {hi}.')
        except ValueError:
            print('Ошибка: требуется целое число.')

def read_enum(prompt: str, enum_cls):
    opts = '/'.join(e.value for e in enum_cls)
    while True:
        val = input(f'{prompt} ({opts}): ').lower()
        for e in enum_cls:
            if val == e.value:
                return e
        print('Неверный ввод.')

def read_yes_no(prompt: str) -> bool:
    while True:
        val = input(f'{prompt} (д/н): ').lower()
        if val in ('д', 'н'):
            return val == 'д'
        print('Введите "д" или "н".')


# Главный код программы

def add_form(cur: sqlite3.Cursor) -> None:
    age = read_int('Возраст: ', 0, 120)
    gender = read_enum('Пол', Gender)
    education = read_enum('Образование \u2013 н-начальное, с-среднее, в-высшее', Education)
    answer = read_yes_no('Вы ежегодно делаете прививку от гриппа?')
    cur.execute(
        'INSERT INTO forms(age, gender, education, answer_yes) VALUES (?,?,?,?)',
        (age, gender.value, education.value, int(answer))
    )
    print('Спасибо, анкета добавлена!')


def list_forms(cur: sqlite3.Cursor) -> None:
    rows: List[tuple] = cur.execute(
        'SELECT age, gender, education, answer_yes FROM forms ORDER BY id'  # keep insertion order
    ).fetchall()
    if not rows:
        print('Список анкет пуст.')
        return
    print('\n--- Все анкеты ---')
    for idx, (age, gender, edu, ans) in enumerate(rows, 1):
        gender_ru = 'муж' if gender == 'м' else 'жен'
        edu_ru = {'н': 'нач', 'с': 'сред', 'в': 'высш'}[edu]
        print(f"{idx:>2}) {age:>3} лет, {gender_ru}, {edu_ru}, ответ={'ДА' if ans else 'НЕТ'}")
    print('------------------')


def show_stats(cur: sqlite3.Cursor) -> None:
    men_40_yes = cur.execute(
        """SELECT COUNT(*) FROM forms
           WHERE gender='м' AND age>40 AND education='в' AND answer_yes=1""").fetchone()[0]

    women_30_no = cur.execute(
        """SELECT COUNT(*) FROM forms
           WHERE gender='ж' AND age<30 AND education='с' AND answer_yes=0""").fetchone()[0]

    men_25_yes = cur.execute(
        """SELECT COUNT(*) FROM forms
           WHERE gender='м' AND age<25 AND education='н' AND answer_yes=1""").fetchone()[0]

    print('\n--- Статистика ---')
    print(f'Мужчин старше 40 с высшим образованием и ответом ДА : {men_40_yes}')
    print(f'Женщин моложе 30 со средним образованием и ответом НЕТ: {women_30_no}')
    print(f'Мужчин моложе 25 с начальным образованием и ответом ДА: {men_25_yes}')
    print('------------------')

# Интерфейс программы  

def menu() -> str:
    print('\nМеню:')
    print('1 – Добавить анкету')
    print('2 – Показать все анкеты')
    print('3 – Показать статистику')
    print('0 – Выход')
    return input('Выбор: ').strip()


def main() -> None:
    conn = open_db()
    cur = conn.cursor()
    try:
        while True:
            choice = menu()
            if choice == '1':
                add_form(cur)
                conn.commit()
            elif choice == '2':
                list_forms(cur)
            elif choice == '3':
                show_stats(cur)
            elif choice == '0':
                break
            else:
                print('Нет такого пункта.')
    finally:
        conn.close()
        print('До свидания!')


if __name__ == '__main__':
    main()