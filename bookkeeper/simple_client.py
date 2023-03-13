"""
Простой тестовый скрипт для терминала
"""

from datetime import datetime
import sys

from PySide6.QtWidgets import QApplication

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.presenter import Bookkeeper
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.view.qtview import QtView
from bookkeeper.utils import read_tree

USE_SQLITE = True

if USE_SQLITE:
    cat_repo = SQLiteRepository[Category]("database.db", Category)
    exp_repo = SQLiteRepository[Expense]("database.db", Expense)
else:
    cat_repo = MemoryRepository[Category]()  # type: ignore[assignment]
    exp_repo = MemoryRepository[Expense]()  # type: ignore[assignment]

    cats = '''
    Продукты
        Мясо
            Сырое мясо
            Мясные продукты
            Рыба
        Молочные изделия
            Кефир
            Сыр
            Сметана
        Сладости
        Хлеб
    Телефон
    Книги
    Одежда
    Хозтовары
    Food
        Meat
            Raw meat
            Fish
        Dairy
            Cheese
            Milk
        Sweets
    '''.lower().splitlines()

    Category.create_from_tree(read_tree(cats), cat_repo)

    CSV = """
    2023-03-12 15:09:00;7.49;Хозтовары;Пакет на кассе
    2023-03-12 15:09:00;104.99;Кефир;
    2023-03-12 15:09:00;129.99;Хлеб;
    2023-03-12 15:09:00;239.98;Сладости;Пряники
    2023-03-12 15:09:00;139.99;Сыр;
    2023-03-12 15:09:00;92.99;Сметана;
    2023-03-09 20:32:02;5536.00;Книги;Книги по python и pyqt
    2023-03-08 23:01:38;478.00;Телефон;
    2023-03-05 14:18:00;78.00;Продукты;
    2023-03-05 14:18:00;1112.00;Рыба;
    """
    exps: list[list[str]] = [s.split(';') for s in CSV.strip().split('\n')]

    for i, (time, amount, name, comment) in enumerate(exps):
        try:
            cat = cat_repo.get_all({'name': name.lower()})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(
            float(amount),
            cat.pk,
            expense_date=datetime.strptime(time, "%Y-%m-%d %H:%M:%S"),
            comment=comment
        )
        exp_repo.add(exp)

app = QApplication(sys.argv)
view = QtView()
bk = Bookkeeper(view, exp_repo, cat_repo)
view.window.show()

sys.exit(app.exec())


CODE = """
while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break

    if not cmd:
        continue

    if cmd in ('категории', "cats"):
        print(*cat_repo.get_all(), sep='\n')
    elif cmd in ('расходы', "exps"):
        print(*exp_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)
"""
