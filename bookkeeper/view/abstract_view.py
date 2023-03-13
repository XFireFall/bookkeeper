"""
Абстрактный класс для приложения Bookkeeper.
"""

from abc import abstractmethod
from typing import Any, Protocol, Callable

from bookkeeper.models.category import Category


class AbstractView(Protocol):
    """
    Абстрактный класс для приложения Bookkeeper.
    """

    def cat_read(self, pk: int) -> Category:
        """
        Костыль для mypy.
        """

        return Category(pk=pk, name="")

    def cat_reads(self, attrs: dict[str, Any]) -> list[Category]:
        """
        Костыль для mypy.
        """

        return [self.cat_read(0)]

    # cat_update: Callable[[Category], None] = lambda self, x: None
    # cat_delete: Callable[[int], None]      = lambda self, x: None

    # exp_create: Callable[[Expense], None] = lambda self, x: None
    # exp_read:   Callable[[int], Expense]  =
    #    lambda self, x: Expense(pk=x, amount=0.0, category=0)
    # exp_reads:  Callable[[dict[str, Any]], list[Expense]] = lambda self, x: []
    # exp_update: Callable[[Expense], None] = lambda self, x: None
    # exp_delete: Callable[[int], None]     = lambda self, x: None

    def register_handlers(
        self,
        name: str,
        **functions: Callable[..., Any]
    ) -> None:
        """
        Зарегистрировать методы доступа к репозиториям.
        """

        for key, value in functions.items():
            setattr(self, name+"_"+key, value)

    def call_crud(
        self,
        func: str,
        *args: Any, **kwargs: Any
    ) -> Any:
        """
        Вызвать метод доступа к репозиториям.
        """

        return getattr(self, func)(*args, **kwargs)

    @abstractmethod
    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Перерисовать с учетом изменений в репозиториях.
        """

    @abstractmethod
    def status(self, text: str) -> None:
        """
        Отобразить текущий статус выполнения программы.
        """
