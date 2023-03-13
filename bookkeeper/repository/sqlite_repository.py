"""
Модуль описывает репозиторий, работающий с базой данных посредством SQLite
"""

from datetime import datetime
from inspect import get_annotations
import sqlite3
from typing import Any

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий в постоянной памяти. Хранит базу данных в файле.
    """

    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')

        self.lastrowid: int | None = 0

        self.cls = cls

        types_py2sql = {
            str: "TEXT",
            int: "INT",
            float: "FLOAT",
            datetime: "TIMESTAMP",
        }

        with sqlite3.connect(
            self.db_file,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        ) as con:
            cur = con.cursor()
            res = cur.execute("SELECT name FROM sqlite_master")
            tables = {i[0] for i in res.fetchall()}
            if self.table_name not in tables:
                names = ', '.join(
                    f"{k} {types_py2sql.get(v, 'INT')}"
                    for k, v in self.fields.items()
                )
                cur.execute(
                    f"CREATE TABLE {self.table_name}({names})"
                )
        con.close()

        fields = ', '.join(self.fields.keys())
        query = ', '.join("?" * len(self.fields))
        upd = ', '.join(f"{k}=?" for k in self.fields.keys())
        self.sql: dict[str, str] = {
            "pragma": "PRAGMA foreign_keys = ON",
            "insert": f"INSERT INTO {self.table_name} ({fields}) VALUES ({query})",
            "select": f"SELECT rowid, * FROM {self.table_name} ",
            "update": f"UPDATE {self.table_name} SET {upd} ",
            "delete": f"DELETE FROM {self.table_name} ",
            "drop": f"DROP TABLE {self.table_name}",
        }

        def where(*keys: str) -> str:
            if not keys:
                return ""
            return "WHERE " + ', '.join(f"{k}=?" for k in keys)
        self.sql_where = where

    def _execute(self, command: str, values: list[Any] | None = None) -> Any:
        with sqlite3.connect(
                    self.db_file,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as con:
            cur = con.cursor()
            if values:
                res = cur.execute(command, list(values))
            else:
                res = cur.execute(command)
            ret, self.lastrowid = res.fetchall(), cur.lastrowid
        con.close()
        return ret

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')

        values = [getattr(obj, x) for x in self.fields]
        self._execute(self.sql["insert"], values)
        if self.lastrowid is None:
            raise RuntimeError(f'trying to add object {obj} failed')
        obj.pk = self.lastrowid
        return obj.pk

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        if where is None:
            where = {}
        res = self._execute(
            self.sql["select"] + self.sql_where(*where.keys()),
            list(where.values())
        )
        objs = []
        for pk, *values in res:
            obj = self.cls(**dict(zip(self.fields.keys(), values)))
            obj.pk = pk
            objs.append(obj)
        return objs

    def get(self, pk: int) -> T | None:
        objs = self.get_all({'rowid': pk})
        return objs[0] if objs else None

    def update(self, obj: T) -> None:
        if getattr(obj, 'pk', None) == 0:
            raise ValueError(f'trying to update object {obj} with zero `pk` attribute')
        self._execute(
            self.sql["update"] + self.sql_where("rowid"),
            [getattr(obj, x) for x in self.fields] + [obj.pk]
        )

    def delete(self, pk: int) -> None:
        res = self._execute(self.sql["select"] + self.sql_where("rowid"), [pk])
        if not res:
            raise KeyError(f'trying to delete unexisting with primary key {pk}')
        self._execute(self.sql["delete"] + self.sql_where("rowid"), [pk])

    def clear(self) -> None:
        """
        Удалить все записи из базы данных
        """

        self._execute(self.sql["delete"])
