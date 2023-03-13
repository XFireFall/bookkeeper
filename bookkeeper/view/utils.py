"""
Полезные функции для PySide6.
"""

from datetime import datetime
from typing import Any, TypeVar, Union

from PySide6 import QtWidgets
from PySide6.QtCore import QDateTime, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator


def double_validator() -> QRegularExpressionValidator:
    """
    Вадидатор числа с плавающей точкой.
    """

    return QRegularExpressionValidator(
        QRegularExpression(r"\d{1,6}(\.\d{0,2})?")
    )


def word_validator() -> QRegularExpressionValidator:
    """
    Вадидатор слова (буквы и пробел).
    """

    return QRegularExpressionValidator(
        QRegularExpression(r"[a-zA-Z ]+")
    )


def words_validator(words: list[str]) -> QRegularExpressionValidator:
    """
    Вадидатор одного из списка слов.
    """

    return QRegularExpressionValidator(
        QRegularExpression('|'.join(words))
    )


T = TypeVar('T', bound=Union[
    QtWidgets.QLayout,
    QtWidgets.QStackedWidget
])


def layout(init: T, *objs: Any) -> T:
    """
    Добавить указанные виждеты к существующей сетке/стеку.
    """

    for obj in objs:
        if isinstance(obj, QtWidgets.QLayout) and hasattr(init, "addLayout"):
            init.addLayout(obj)
        else:
            init.addWidget(obj)
    return init


def vbox(*objs: Any) -> QtWidgets.QVBoxLayout:
    """
    Создать QVBoxLayout из указанных виджетов.
    """

    return layout(QtWidgets.QVBoxLayout(), *objs)


def hbox(*objs: Any) -> QtWidgets.QHBoxLayout:
    """
    Создать QHBoxLayout из указанных виджетов.
    """

    return layout(QtWidgets.QHBoxLayout(), *objs)


def stack(*objs: Any) -> QtWidgets.QStackedWidget:
    """
    Создать QStackedWidget из указанных виджетов.
    """

    return layout(QtWidgets.QStackedWidget(), *objs)


def grid(objs: list[list[Any]]) -> QtWidgets.QGridLayout:
    """
    Создать сетку из матрицы виджетов.
    """

    init = QtWidgets.QGridLayout()
    for row, _objs in enumerate(objs):
        for col, obj in enumerate(_objs):
            if obj is None:
                continue
            if isinstance(obj, QtWidgets.QLayout):
                init.addLayout(obj, row, col)
            else:
                init.addWidget(obj, row, col)
    return init


datetime_formats = {
    "Qt": "yyyy-MM-dd hh:mm:ss",
    "datetime": "%Y-%m-%d %H:%M:%S",
}


def str2datetime(time: str) -> datetime:
    """
    строка -> формат datetime
    """

    return datetime.strptime(time, datetime_formats["datetime"])


def str2qdatetime(time: str) -> QDateTime:
    """
    строка -> формат QDateTime
    """

    return QDateTime.fromString(time, datetime_formats["Qt"])


def datetime2str(time: datetime) -> str:
    """
    формат datetime -> строка
    """

    return time.strftime(datetime_formats["datetime"])


def datetime2qdatetime(time: datetime) -> QDateTime:
    """
    формат datetime -> формат QDateTime
    """

    return str2qdatetime(datetime2str(time))


def qdatetime2str(time: QDateTime) -> str:
    """
    формат QDateTime -> строка
    """

    return time.toString(datetime_formats["Qt"])


def qdatetime2datetime(time: QDateTime) -> datetime:
    """
    формат QDateTime -> формат datetime
    """

    return str2datetime(qdatetime2str(time))
