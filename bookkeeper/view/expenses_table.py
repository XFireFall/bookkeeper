"""
Отображение и редактирование записей расходов.
"""

from typing import Any, Callable
from datetime import datetime

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView

from bookkeeper.models.expense import Expense
from bookkeeper.view import utils


class ExpensesTable(QtWidgets.QTableWidget):
    """
    Таблица с возможностью выбора одной ячейки.
    """

    def __init__(
        self,
        del_row: Callable[[int], None],
        *args: Any, **kwargs: Any
    ):
        super().__init__(3, 4, *args, **kwargs)
        self.del_row = del_row
        self.menu = QtWidgets.QMenu()

    def contextMenuEvent(self, *args: Any, **kwargs: Any) -> None:
        super().contextMenuEvent(*args, **kwargs)

        if not self.selectionModel().selection().indexes():
            return
        for i in self.selectionModel().selection().indexes():
            row = i.row()
        self.menu = QtWidgets.QMenu()
        delete_action = self.menu.addAction("Удалить запись расхода")
        delete_action.triggered.connect(  # type: ignore[attr-defined]
            lambda: self.del_row(row)
        )
        self.menu.popup(QtGui.QCursor().pos())


class ExpensesWidget(QtWidgets.QWidget):
    """
    Таблица расходов с возможностью удаления и редактирования записей.
    """

    delete_expense: QtCore.Signal = QtCore.Signal(int)
    update_expense: QtCore.Signal = QtCore.Signal(Expense, str, object)

    def __init__(
        self,
        pk2cat: Callable[[int], str],
        cat2pk: Callable[[str], int],
        get_exps: Callable[[], list[Expense]],
        get_cats: Callable[[], list[str]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.get_exps = get_exps

        self.datetime_edit = QtWidgets.QDateTimeEdit(  # type: ignore[call-overload]
            self, calendarPopup=True
        )
        self.datetime_edit.setDateTime(utils.datetime2qdatetime(datetime.now()))
        self.datetime_edit.setEnabled(False)
        self.datetime_edit.connected = False

        self.table = ExpensesTable(lambda row: self.delete_expense.emit(
            self.displayed[row].pk
        ))
        self.table.setHorizontalHeaderLabels(
            "Дата|Сумма|Категория|Комментарий".split('|')
        )
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked  # type: ignore[attr-defined]
        )
        self.table.cellDoubleClicked.connect(  # type: ignore[attr-defined]
            self.double_click
        )
        self.table.verticalHeader().hide()

        class ItemDelegate(QtWidgets.QStyledItemDelegate):
            """
            Этого никто не увидит.
            """

            def __init__(
                self,
                get_words: Callable[[], list[str]],
                *args: Any, **kwargs: Any
            ):
                super().__init__(*args, **kwargs)
                self.get_words = get_words

            def createEditor(self, parent: Any, option: Any, index: Any) -> Any:
                editor = super().createEditor(parent, option, index)
                if index.column() == 1:
                    editor.setValidator(  # type: ignore[attr-defined]
                        utils.double_validator()
                    )
                elif index.column() == 2:
                    editor.setValidator(  # type: ignore[attr-defined]
                        utils.words_validator(self.get_words())
                    )
                return editor

        self.table.setItemDelegate(ItemDelegate(get_cats, self.table))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents  # type: ignore[attr-defined]
        )
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents  # type: ignore[attr-defined]
        )
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents  # type: ignore[attr-defined]
        )
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
        )

        self.setLayout(utils.vbox(
            utils.hbox(
                QtWidgets.QLabel("Последние расходы"), self.datetime_edit
            ),
            self.table
        ))

        self.text2expenseattr: dict[str, Callable[[str], Any]] = {
            "expense_date": utils.str2datetime,
            "amount": float,
            "category": cat2pk,
            "comment": str,
        }
        self.col2attr = list(self.text2expenseattr.keys())

        self.expense2texts: Callable[[Expense], tuple[str, str, str, str]] = lambda exp: (
            utils.datetime2str(exp.expense_date),
            f"{exp.amount:.2f}",
            pk2cat(exp.category),
            exp.comment,
        )

        self.displayed: list[Expense] = []

    def double_click(self, row: int, col: int) -> None:
        """
        Обработать двойноу нажатие по таблице.
        """

        if col == 0:
            if self.datetime_edit.connected:
                self.datetime_edit.connected = False
                self.datetime_edit.dateTimeChanged.disconnect()

            self.datetime_edit.setDateTime(
                utils.str2qdatetime(self.table.item(row, col).text())
            )
            self.datetime_edit.setEnabled(True)
            self.datetime_edit.setFocus()
            self.datetime_edit.connected = True
            self.datetime_edit.dateTimeChanged.connect(
                lambda time: self.update_expense.emit(
                    self.displayed[row],
                    "expense_date",
                    utils.qdatetime2datetime(time)
                )
            )
        else:
            self.table.cellChanged.connect(  # type: ignore[attr-defined]
                self.cell_changed
            )

    def cell_changed(self, row: int, col: int) -> None:
        """
        Обновить сумму/категорию/заметку записи расхода, выбранной в таблице.
        """

        self.table.cellChanged.disconnect(self.cell_changed)  # type: ignore[attr-defined]
        attr = self.col2attr[col]
        self.update_expense.emit(
            self.displayed[row],
            attr,
            self.text2expenseattr[attr](self.table.item(row, col).text())
        )

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)

        entries = sorted(
            self.get_exps(),
            key=lambda exp: exp.expense_date,
            reverse=True
        )

        self.table.setRowCount(len(entries))
        self.displayed = []
        for row, exp in enumerate(entries):
            self.displayed.append(exp)
            for col, text in enumerate(self.expense2texts(exp)):
                item = QtWidgets.QTableWidgetItem(text)
                if col == 0:
                    item.setFlags(
                        Qt.ItemIsSelectable  # type: ignore[attr-defined]
                        | Qt.ItemIsEnabled  # type: ignore[attr-defined]
                    )
                self.table.setItem(row, col, item)

        self.datetime_edit.setEnabled(False)
        if self.datetime_edit.connected:
            self.datetime_edit.connected = False
            self.datetime_edit.dateTimeChanged.disconnect()
