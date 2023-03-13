"""
AbstractView, реализованный с помощью PySide6.
"""

from typing import Any, Callable

from PySide6 import QtWidgets

from bookkeeper.view.abstract_view import AbstractView
from bookkeeper.view.main_widget import MainWidget
from bookkeeper.view.secondary_widget import SecondaryWidget
from bookkeeper.view.utils import stack


class QtView(AbstractView):
    """
    AbstractView, реализованный с помощью PySide6.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self._status = QtWidgets.QStatusBar()

        def handler(func: str) -> Callable[..., Any]:
            return lambda *args, **kwargs: self.call_crud(func, *args, **kwargs)

        def pk2cat(pk: int) -> str:
            return self.cat_read(pk).name

        def cat2pk(name: str) -> int:
            return self.cat_reads({"name": name})[0].pk

        self.main = MainWidget(
            pk2cat,
            cat2pk,
            handler("exp_reads"),
            handler("cat_reads")
        )
        self.main.add_expense.connect(handler("exp_create"))
        self.main.update_expense.connect(handler("exp_update"))
        self.main.delete_expense.connect(handler("exp_delete"))
        self.main.button_edit_categories.connect(self.switch)

        self.second = SecondaryWidget(
            lambda: [cat.name for cat in handler("cat_reads")()]
        )
        self.second.add_category.connect(handler("cat_create"))
        self.second.delete_category.connect(handler("cat_delete"))
        self.second.button_return.connect(self.switch)

        self.stack = stack(self.main, self.second)

        self.current_widget = "main"
        # self.current_widget = "second"
        self.stack.setCurrentWidget(
            self.main if self.current_widget == "main" else self.second
        )

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("The Bookkeeper App")
        self.window.resize(700, 500)
        self.window.setStatusBar(self._status)
        self.window.setCentralWidget(self.stack)

    def update(self, text: str = "...") -> None:
        self.window.update()
        self.main.update()
        self.second.update()
        self.status(text)

    def status(self, text: str) -> None:
        self._status.showMessage(text)

    def switch(self) -> None:
        """
        Переключиться между главными виджетами (расходы <-> категории).
        """

        if self.current_widget == "main":
            self.current_widget = "second"
            self.stack.setCurrentWidget(self.second)
        elif self.current_widget == "second":
            self.current_widget = "main"
            self.stack.setCurrentWidget(self.main)
        self.update()
