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

filename = "/tmp/cloudmesh.yaml"

data = {
    "a": "1",
    "b": "2",
    "c": {"c1": 3, "c2": 3, }
}


@pytest.mark.incremental
class TestConfig:

    def test_YamlDB(self):
        HEADING()
        db = YamlDB(data, filename=filename)
        print(db.data)
        db.save()
        assert "a" in db.data

    def test_if_yaml_file_exists(self):
        HEADING()
        YamlDB(data=data, filename=filename)
        assert os.path.isfile(filename)

    def test_dict(self):
        HEADING()
        db = YamlDB(data=data, filename=filename)
        StopWatch.start("dict")
        result = db.dict()
        StopWatch.stop("dict")
        pprint(result)
        print(db)
        print(type(db.data))

    def test_subscription(self):
        HEADING()
        db = YamlDB(data=data, filename=filename)
        assert db.data["c"]["c1"] == 3

    def test_get(self):
        HEADING()
        StopWatch.start("get")
        db = YamlDB(data=data, filename=filename)
        a = db["a"]
        StopWatch.stop("get")
        print(db)
        assert a == "1"

    def test_set(self):
        HEADING()
        StopWatch.start("set")
        db = YamlDB(data=data, filename=filename)
        db["cloudmesh.test.nested"] = "Gregor"
        StopWatch.stop("set")
        print(db["cloudmesh.test.nested"])
        assert db["cloudmesh.test.nested"] == "Gregor"

    def test_doesnotexist_key(self):
        HEADING()
        db = YamlDB(data=data, filename=filename)

        key = "cloudmesh.doesnotexist"
        StopWatch.start(f"db[{key}]")
        try:
            db[key]
            result = True
        except:
            result = False
        StopWatch.stop(f"db[{key}]")

        assert result is False

    def test_doesnotexist_get(self):
        HEADING()
        db = YamlDB(data=data, filename=filename)

        key = "cloudmesh.doesnotexist"
        StopWatch.start(f"db.get({key})")
        value = db.get(key, default="Hallo")
        StopWatch.stop(f"db.get({key})")

        print(db.data)

        assert value == "Hallo"

    '''
    def test_search(self):
        db = YamlDB(data=data, filename=filename)

        StopWatch.start("search")
        r = db.search("c.*", True)
        StopWatch.stop("search")
        pprint (r)

        assert db is not None
    '''

    def test_StopWatch(self):
        StopWatch.benchmark(sysinfo=False)
