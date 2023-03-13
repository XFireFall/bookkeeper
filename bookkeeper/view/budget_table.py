"""
Отображение бюджета.
"""

from datetime import datetime, timedelta
from typing import Any, Callable

from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from bookkeeper.models.expense import Expense
from bookkeeper.view import utils


class BudgetWidget(QtWidgets.QWidget):
    """
    Таблица для отображения текущего бюджета.
    """

    def __init__(
        self,
        get_exps: Callable[[], list[Expense]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.get_exps = get_exps

        self.table = QtWidgets.QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels("|Сумма|Бюджет".split('|'))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents  # type: ignore[attr-defined]
        )
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
        )
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
        )

        header = self.table.verticalHeader()
        for i in range(3):
            header.setSectionResizeMode(
                i, QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
            )

        self.table.verticalHeader().hide()

        for i, text in enumerate("День Неделя Месяц".split()):
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(
                Qt.ItemIsSelectable  # type: ignore[attr-defined]
                | Qt.ItemIsEnabled  # type: ignore[attr-defined]
            )
            self.table.setItem(i, 0, item)

        for i in range(3):
            item = QtWidgets.QTableWidgetItem()
            self.table.setItem(i, 2, item)

        class ItemDelegate(QtWidgets.QStyledItemDelegate):
            """
            Этого никто не увидит.
            """

            def createEditor(self, parent: Any, option: Any, index: Any) -> Any:
                editor = super().createEditor(parent, option, index)
                if index.column() == 2:
                    editor.setValidator(  # type: ignore[attr-defined]
                        utils.double_validator()
                    )
                return editor
        self.table.setItemDelegate(ItemDelegate(self.table))

        self.setLayout(utils.vbox(
            QtWidgets.QLabel("Бюджет"),
            self.table
        ))

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)

        today = datetime.today()
        for i, days in enumerate([1, 7, 31]):
            amount = sum(
                exp.amount
                for exp in self.get_exps()
                if today - exp.expense_date < timedelta(**{"days": days})
            )
            item = QtWidgets.QTableWidgetItem(f"{amount:.2f}")
            item.setFlags(
                Qt.ItemIsSelectable  # type: ignore[attr-defined]
                | Qt.ItemIsEnabled  # type: ignore[attr-defined]
            )
            self.table.setItem(i, 1, item)
