###############################################################
# pytest -v --capture=no tests/test_config.py
# pytest -v  tests/test_config.py
# pytest -v --capture=no  tests/test_config..py::Test_config::<METHODNAME>
###############################################################

import os
from pprint import pprint

import pytest
from yamldb.YamlDB import YamlDB

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import readfile
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import path_expand

if os_is_windows():
    filename = "~/.cloudmesh/cloudmesh.yaml"
else:
    filename = "/tmp/cloudmesh.yaml"

filename = path_expand(filename)

data = {
    "a": 1,
    "b": "text",
    "c": {
        "c1": "c",
        "c2": "cc",
    },
}


@pytest.mark.incremental
class TestConfig:
    def test_01_init(self):
        HEADING()
        StopWatch.start("init")
        db = YamlDB(data=data, filename=filename)
        StopWatch.stop("init")
        db.save()
        content = readfile(filename)
        print(db.data)
        print(content)

        assert "a" in db.data
        assert db.data["c"]["c1"] == "c"
        assert os.path.isfile(filename)

    def test_02_read(self):
        HEADING()
        StopWatch.start("read")
        db = YamlDB(filename=filename)
        db.load(filename=filename)
        StopWatch.stop("read")
        assert type(db["a"]) == int
        assert "a" in db.data

    def test_03_dict(self):
        HEADING()
        db = YamlDB(filename=filename)
        StopWatch.start("dict")
        result = db.dict()
        StopWatch.stop("dict")
        pprint(result)
        print(db)
        print(type(db.data))
        assert "a" in result
        assert "c.c1" in db

    def test_04_set_nested(self):
        HEADING()
        StopWatch.start("set")
        db = YamlDB(filename=filename)
        db["cloudmesh.test.nested"] = "Gregor"
        StopWatch.stop("set")
        print(db["cloudmesh.test.nested"])
        assert db["cloudmesh.test.nested"] == "Gregor"

    def test_05_doesnotexist_key(self):
        HEADING()
        db = YamlDB(filename=filename)

        key = "cloudmesh.doesnotexist"
        StopWatch.start(f"db[{key}]")
        try:
            db[key]
            result = True
        except:
            result = False
        StopWatch.stop(f"db[{key}]")

        assert result is False

    def test_06_get_create(self):
        HEADING()
        db = YamlDB(filename=filename)

        key = "cloudmesh.doesnotexist"
        StopWatch.start(f"db.get({key})")
        value = db.get(key, default="Hallo")
        StopWatch.stop(f"db.get({key})")

        print(db)

        assert value == "Hallo"

    def test_07_search(self):
        db = YamlDB(data=data, filename=filename)

        StopWatch.start("search")
        r = db.search("c.*")
        StopWatch.stop("search")
        pprint(r)
        assert ["c", "cc"] == r
        assert db is not None

    def test__08_set_does_not_exist(self):
        HEADING()
        db = YamlDB(filename=filename)
        key = "cloudmesh.doesnotexist"

        db["cloudmesh.test.a"] = "aa"
        print(db)

        StopWatch.start("delete")
        db.delete("a")  # does not throw exception
        print(db)

        assert "cloudmesh.test" in db
        db.delete("cloudmesh.test")
        print(db)
        assert "cloudmesh.test" not in db  # this is a bug

        del db[key]
        StopWatch.stop("delete")
        assert "a" not in db
        assert "cloudmesh.doesnotexist" not in db

    def test_09_StopWatch(self):
        StopWatch.benchmark(sysinfo=False)
