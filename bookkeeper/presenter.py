"""
Presenter для MVP модели приложения Bookkeeper.
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.view.abstract_view import AbstractView


class Bookkeeper:
    """
    Presenter для MVP модели приложения Bookkeeper.
    """

    def __init__(
        self,
        view: AbstractView,
        exp_repo: AbstractRepository[Expense],
        cat_repo: AbstractRepository[Category]
    ):
        self.exp_repo = exp_repo
        self.cat_repo = cat_repo

        def _cat2pk(name: str) -> int | None:
            cats = cat_repo.get_all({"name": name})
            return cats[0].pk if cats else None
        self.cat2pk = _cat2pk

        self.view = view
        self.view.register_handlers(
            "exp",
            create=self.add_expense,
            read=self.exp_repo.get,
            reads=self.exp_repo.get_all,
            update=self.update_expense,
            delete=self.delete_expense
        )

        self.view.register_handlers(
            "cat",
            create=self.add_category,
            read=self.cat_repo.get,
            reads=self.cat_repo.get_all,
            delete=self.delete_category
        )

        self.view.update()

    def add_category(self, name: str, parent: str) -> None:
        """
        Добавить категорию + перерисовать.
        """

        if not name:
            self.view.status("Укажите название новой категории!")
            return

        if self.cat_repo.get_all({"name": name}):
            self.view.status(f"Категория [{name}] уже существует!")
            return

        if parent == "":
            parent_pk = None
        else:
            parent_pk = self.cat2pk(parent)
            if parent_pk is None:
                self.view.status("Укажите правильного родителя!")
                return

        self.cat_repo.add(Category(name, parent_pk))
        self.view.update(f"Создана категория [{name}].")

    def delete_category(self, name: str) -> None:
        """
        Удалить категорию (и изменить соответствубщие записи) + перерисовать.
        """

        cat = self.cat_repo.get_all({"name": name})[0]
        cat_pk = cat.pk
        parent_pk = cat.parent

        exps = self.exp_repo.get_all({"category": cat_pk})
        cats = self.cat_repo.get_all({"parent": cat_pk})
        if parent_pk is None:
            for exp in exps:
                self.exp_repo.delete(exp.pk)
            for cat in cats:
                cat.parent = None
                self.cat_repo.update(cat)
        else:
            for exp in exps:
                exp.category = parent_pk
                self.exp_repo.update(exp)
            for cat in cats:
                cat.parent = parent_pk
                self.cat_repo.update(cat)

        self.cat_repo.delete(cat_pk)
        self.view.update(f"Категория [{name}] удалена.")

    def add_expense(self, amount: float, name: str) -> None:
        """
        Добавить запись расхода + перерисовать.
        """

        cat = self.cat_repo.get_all({"name": name})
        if not cat:
            self.view.status("Укажите правильного родителя!")
            return
        self.exp_repo.add(Expense(amount, cat[0].pk))
        self.view.update("Добавлена запись расходов.")

    def update_expense(self, exp: Expense, attr: str, value: object) -> None:
        """
        Обновить запись расхода + перерисовать.
        """

        setattr(exp, attr, value)
        self.exp_repo.update(exp)
        self.view.update("Запись расходов обновлена.")

    def delete_expense(self, pk: int) -> None:
        """
        Удалить запись расхода + перерисовать.
        """

        self.exp_repo.delete(pk)
        self.view.update("Запись расходов удалена.")
