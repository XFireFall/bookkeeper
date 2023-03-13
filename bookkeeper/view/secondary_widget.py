"""
Управление категориями.
"""

from typing import Any, Callable

from PySide6 import QtCore, QtWidgets, QtGui

from bookkeeper.view import utils


class CategoryTable(QtWidgets.QTableWidget):
    """
    Таблица с возможностью выбора нескольких ячеек.
    """

    def __init__(
        self,
        del_cell: Callable[[tuple[int, int]], None],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.del_cell = del_cell

        self.menu = QtWidgets.QMenu()

    def contextMenuEvent(self, *args: Any, **kwargs: Any) -> None:
        super().contextMenuEvent(*args, **kwargs)

        if not self.selectionModel().selection().indexes():
            return
        idxs = [
            (i.row(), i.column())
            for i in self.selectionModel().selection().indexes()
        ]
        self.menu = QtWidgets.QMenu()
        delete_action = self.menu.addAction(
            "Удалить категори" + ("и" if len(idxs) > 1 else "ю")
        )
        for idx in idxs:
            delete_action.triggered.connect(  # type: ignore[attr-defined]
                lambda: self.del_cell(idx)
            )
        self.menu.popup(QtGui.QCursor().pos())


class CategoryInput(QtWidgets.QWidget):
    """
    Виджет для добавления и удаления категорий.
    """

    add_category: QtCore.Signal = QtCore.Signal(str, str)
    delete_category: QtCore.Signal = QtCore.Signal(str)

    def __init__(
        self,
        get_cats: Callable[[], list[str]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.get_cats = get_cats

        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText("Наименование")
        self.name.setValidator(utils.word_validator())

        self.cat_parent = QtWidgets.QLineEdit()
        self.cat_parent.setPlaceholderText("Родитель")
        self.cat_parent.textChanged.connect(  # type: ignore[attr-defined]
            lambda: self.update()
        )

        self.submit = QtWidgets.QPushButton("Добавить")
        self.submit.clicked.connect(  # type: ignore[attr-defined]
            lambda: self.add_category.emit(
                self.name.text(),
                self.cat_parent.text()
            )
        )

        self.table_width = 5
        self.table = CategoryTable(
            lambda idx:
                self.delete_category.emit(self.displayed[idx])
                if idx in self.displayed
                else None,
            5, self.table_width
        )
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.cellDoubleClicked.connect(  # type: ignore[attr-defined]
            self.double_click
        )

        self.setLayout(utils.vbox(
            QtWidgets.QLabel("Добавить новую категорию"),
            utils.grid([[
                QtWidgets.QLabel("Новая категория:"), self.name,
            ], [
                QtWidgets.QLabel("Родитель:"), self.cat_parent
            ]]),
            QtWidgets.QLabel("Возможные варианты:"),
            self.table,
            self.submit
        ))

    def double_click(self, row: int, col: int) -> None:
        """
        Двойное нажатие на ячейку таблицы - заполнить полу ввода родителя.
        """

        idx = (row, col)
        if idx not in self.displayed:
            return
        self.cat_parent.setText(self.displayed[idx])

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)

        cats = [
            cat
            for cat in self.get_cats()
            if cat.startswith(self.cat_parent.text())
        ]

        height = (len(cats) + self.table_width - 1) // self.table_width
        self.table.setRowCount(0)
        self.table.setRowCount(height)

        self.displayed = {}
        for cat_no, cat in enumerate(cats):
            row, col = cat_no // self.table_width, cat_no % self.table_width
            item = QtWidgets.QTableWidgetItem(cat)
            self.table.setItem(row, col, item)
            self.displayed[(row, col)] = cat

        header = self.table.horizontalHeader()
        for i in range(self.table_width):
            header.setSectionResizeMode(
                i, QtWidgets.QHeaderView.Stretch  # type: ignore[attr-defined]
            )

        self.cat_parent.setValidator(utils.words_validator(self.get_cats()))


class SecondaryWidget(QtWidgets.QWidget):
    """
    Виджет-окно для редактирования категорий + кнопка "Назад".
    """

    add_category: QtCore.Signal = QtCore.Signal(str, str)
    delete_category: QtCore.Signal = QtCore.Signal(str)

    button_return: QtCore.Signal = QtCore.Signal()

    def __init__(
        self,
        get_cats: Callable[[], list[str]],
        *args: Any, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)

        self.input = CategoryInput(get_cats)
        self.input.add_category.connect(self.add_category.emit)
        self.input.delete_category.connect(self.delete_category.emit)

        self.back = QtWidgets.QPushButton("Назад")
        self.back.clicked.connect(  # type: ignore[attr-defined]
            self.button_return.emit
        )

        self.setLayout(utils.vbox(
            self.input,
            self.back
        ))

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.input.update()
