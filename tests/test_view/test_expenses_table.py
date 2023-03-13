
from bookkeeper.view.expenses_table import ExpensesWidget
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.utils import read_tree

import pytest
from pytestqt.qt_compat import qt_api


@pytest.fixture
def cat_repo():
	repo = MemoryRepository[Category]()
	
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

	Category.create_from_tree(read_tree(cats), repo)
	
	return repo


@pytest.fixture
def exp_repo(cat_repo):
	time_fmt = "%Y-%m-%d %H:%M:%S"
	
	exps = """
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

	exps = exps.strip().split('\n')
	exps = [s.split(';') for s in exps]
	#print(exps)

	#locale = QLocale(QLocale.English, QLocale.UnitedStates) # dot instead of comma

	from datetime import datetime

	repo = MemoryRepository[Expense]()
	for i, (time, amount, cat, comment) in enumerate(exps):
		time = datetime.strptime(time, time_fmt)
		amount = float(amount)
		try:
			cat = cat_repo.get_all({'name': cat.lower()})[0]
		except IndexError:
			print(f'категория {cat} не найдена')
			continue
		exp = Expense(amount, cat.pk, expense_date=time, comment=comment)
		repo.add(exp)
	return repo


def test_hello(qtbot, cat_repo, exp_repo):
	cat2pk = lambda name: cat_repo.get_all({"name": name})[0].pk
	
	widget = ExpensesWidget(
		lambda pk: cat_repo.get(pk).name, cat2pk,
		exp_repo.get_all, lambda: [cat.name for cat in cat_repo.get_all()]
	)
	widget.update_expense.connect(lambda *args: print(args))
	widget.delete_expense.connect(lambda *args: print(args))
	
	qtbot.addWidget(widget)
	
	qtbot.mouseClick(
		widget.table,
		qt_api.QtCore.Qt.MouseButton.LeftButton
	)
