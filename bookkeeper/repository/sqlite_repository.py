from inspect import get_annotations
import sqlite3
from itertools import starmap

from bookkeeper.repository.abstract_repository import AbstractRepository, T


def obj_from_attrs(cls: type, attrs: dict, values):
	obj = cls()
	for attr, value in zip(attrs, values):
		setattr(obj, attr, value)
	return obj


class SQLiteRepository(AbstractRepository[T]):
	def __init__(self, db_file: str, cls: type) -> None:
		self.db_file = db_file
		self.table_name = cls.__name__.lower()
		self.fields = get_annotations(cls, eval_str=True)
		self.fields.pop('pk')
		self.cls = cls
		
		with sqlite3.connect(self.db_file) as con:
			cur = con.cursor()
			res = cur.execute("SELECT name FROM sqlite_master")
			tables = {i[0] for i in res.fetchall()}
			if self.table_name not in tables:
				names = ', '.join(self.fields.keys())
				cur.execute(
					f"CREATE TABLE {self.table_name}({names})"
				)
		con.close()

	def add(self, obj: T) -> int:
		names = ', '.join(self.fields.keys())
		p = ', '.join("?" * len(self.fields))
		values = [getattr(obj, x) for x in self.fields]
		with sqlite3.connect(self.db_file) as con:
			cur = con.cursor()
			cur.execute("PRAGMA foreign_keys = ON")
			cur.execute(
				f"INSERT INTO {self.table_name} ({names}) VALUES ({p})",
				values
			)
			obj.pk = cur.lastrowid
		con.close()
		return obj.pk
	
	def get(self, pk: int) -> T | None:
		with sqlite3.connect(self.db_file) as con:
			cur = con.cursor()
			res = cur.execute(f"SELECT * FROM {self.table_name} where rowid={pk}")
			res = res.fetchone()
			if res:
				obj = obj_from_attrs(self.cls, self.fields.keys(), res)
				obj.pk = pk
			else:
				obj = None
		con.close()
		return obj

	def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
		query = ", ".join(f"{k} = {repr(v)}" for k, v in where.items())
		if query:
			query = "WHERE " + query
		with sqlite3.connect("test-1.db") as con:
			cur = con.cursor()
			res = cur.execute(f"SELECT rowid, * FROM {self.table_name} {query}")
			objs = [
				obj_from_attrs(self.cls, ["pk"] + list(self.fields.keys()), values)
				for values in res.fetchall()
			]
		con.close()
		return objs

	def update(self, obj: T) -> None:
		p = ', '.join(attr+"=?" for attr in self.fields.keys())
		values = [getattr(obj, x) for x in self.fields]
		with sqlite3.connect("test-1.db") as con:
			cur = con.cursor()
			cur.execute(
				f"UPDATE {self.table_name} SET {p} WHERE rowid={obj.pk}",
				values
			)
		con.close()
	
	def delete(self, pk: int) -> None:
		with sqlite3.connect("test-1.db") as con:
			cur = con.cursor()
			cur.execute(f"DELETE FROM {self.table_name} WHERE rowid={pk}")
		con.close()
