"""
Отображение и редактирование расходов.
"""

from typing import Any, Callable

from PySide6 import QtWidgets, QtCore

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.view import utils
from bookkeeper.view.budget_table import BudgetWidget
from bookkeeper.view.expenses_table import ExpensesWidget


class ExpenseInput(QtWidgets.QWidget):
    """
    Добавление записи расхода.
    """

    add_expense: QtCore.Signal = QtCore.Signal(float, str)

    def __init__(
        self,
        get_cats: Callable[[], list[Category]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.get_cats = get_cats

        self.amount = QtWidgets.QLineEdit("")
        self.amount.setValidator(utils.double_validator())
        self.amount.setPlaceholderText("Сумма покупки")

        self.cats = QtWidgets.QComboBox()

        self.submit = QtWidgets.QPushButton("Добавить")
        self.submit.clicked.connect(  # type: ignore[attr-defined]
            lambda: self.add_expense.emit(
                float(self.amount.text() or "0"),
                self.cats.currentText().strip()
            )
        )

        self.setLayout(utils.grid([[
                QtWidgets.QLabel("Сумма"), self.amount,
            ], [
                QtWidgets.QLabel("Категория"), self.cats,
            ], [
                None, self.submit,
            ]])
        )

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)

        hierarchy: dict[int, list[str]] = {}
        for i in self.get_cats():
            if i.parent is None:
                hierarchy[i.pk] = [i.name]
            else:
                hierarchy[i.pk] = hierarchy[i.parent] + [i.name]
        cats = [
            "  "*(len(i)-1) + i[-1]
            for i in sorted(list(hierarchy.values()), key='.'.join)
        ]

        self.amount.setText("")
        self.cats.clear()
        self.cats.addItems(cats)


class MainWidget(QtWidgets.QWidget):
    """
    Отображение и редактирование расходов
        + кнопка переключения на редактирование категорий.
    """

    add_expense: QtCore.Signal = QtCore.Signal(float, str)
    delete_expense: QtCore.Signal = QtCore.Signal(int)
    update_expense: QtCore.Signal = QtCore.Signal(Expense, str, object)

    button_edit_categories: QtCore.Signal = QtCore.Signal()

    def __init__(
        self,
        pk2cat: Callable[[int], str],
        cat2pk: Callable[[str], int],
        get_exps: Callable[[], list[Expense]],
        get_cats: Callable[[], list[Category]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.expenses = ExpensesWidget(
            pk2cat, cat2pk,
            get_exps=get_exps,
            get_cats=lambda: [cat.name for cat in get_cats()]
        )
        self.expenses.delete_expense.connect(self.delete_expense.emit)
        self.expenses.update_expense.connect(self.update_expense.emit)

        self.budget = BudgetWidget(get_exps)

        self.input = ExpenseInput(get_cats)
        self.input.add_expense.connect(self.add_expense.emit)

        self.edit_cats = QtWidgets.QPushButton("Редактировать")
        self.edit_cats.clicked.connect(  # type: ignore[attr-defined]
            self.button_edit_categories.emit
        )

        self.setLayout(utils.vbox(
            self.expenses,
            self.budget,
            utils.hbox(self.input, self.edit_cats)
        ))

        self.signal = QtCore.Signal(int, QtWidgets.QWidget)

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        for widget in (self.expenses, self.budget, self.input):
            widget.update()
