from bookkeeper.repository.sqlite_repository import SQLiteRepository

import pytest

from datetime import datetime

from dataclasses import dataclass

import os

@dataclass
class Custom():
	pk: int = 0
	s: str = "abcd"
	n: int = 1234
	f: float = 12.34
	t: datetime = datetime.now()


@pytest.fixture
def custom_class():
	return Custom


@pytest.fixture
def repo():
	path = "test_sqlite_repository.db"
	if os.path.exists(path):
		os.unlink(path)
	r = SQLiteRepository(path, Custom)
	r.clear()
	return r


def test_crud(repo, custom_class):
	obj = custom_class()
	pk = repo.add(obj)
	assert obj.pk == pk
	assert repo.get(pk) == obj, (repo.get(pk), obj)
	
	obj2 = custom_class()
	obj2.pk = pk
	repo.update(obj2)
	assert repo.get(pk) == obj2
	
	repo.delete(pk)
	assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
	obj = custom_class()
	obj.pk = 1
	with pytest.raises(ValueError):
		repo.add(obj)


def test_cannot_add_without_pk(repo):
	with pytest.raises(ValueError):
		repo.add(0)


def test_cannot_delete_unexistent(repo):
	with pytest.raises(KeyError):
		repo.delete(1)


def test_cannot_update_without_pk(repo, custom_class):
	obj = custom_class()
	with pytest.raises(ValueError):
		repo.update(obj)


def test_get_all(repo, custom_class):
	objects = [custom_class() for i in range(5)]
	for o in objects:
		repo.add(o)
	print(repo.get_all(), objects)
	assert repo.get_all() == objects


def test_get_all_with_condition(repo, custom_class):
	objects = []
	for i in range(5):
		o = custom_class()
		o.n = i
		o.s = 'test'
		o.t = datetime.now()
		repo.add(o)
		objects.append(o)
	assert repo.get_all({'t': objects[0].t}) == [objects[0]]
	assert repo.get_all({'s': 'test'}) == objects

def test_clear(repo, custom_class):
	obj = custom_class()
	pk = repo.add(obj)
	repo.clear()
	with pytest.raises(KeyError):
		repo.delete(pk)
