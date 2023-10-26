###############################################################
# pytest -v --capture=no tests/test_delete.py
# pytest -v  tests/test_delete.py
# pytest -v --capture=no  tests/test_delete..py::test_delete::<METHODNAME>
###############################################################

import os
from pprint import pprint

import pytest
from yamldb.YamlDB import YamlDB
import yaml

from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import readfile
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner

if os_is_windows():
    filename = "~/.cloudmesh/cloudmesh.yaml"
else:
    filename = "/tmp/cloudmesh.yaml"

filename = path_expand(filename)


data = {
    "floor": {
        "key": "value",
        "key_a": "value_a",
        "key_b": "value_b"
    }
}

def create_data_file(filename, data):
    with open(filename, 'w') as file:
        yaml.dump(dict(data), file)

@pytest.mark.incremental
class TestConfig:

    def test_delete(self):
        HEADING()
        global data
        print (data)
        assert os.path.isfile(filename)

        StopWatch.start("init")
        db = YamlDB(data=dict(data), filename=filename)
        StopWatch.stop("init")
        db.save()
        content = readfile(filename)
        banner("content")
        print(content)
        banner("db.data")
        print(db)
        banner("value")
        print (db["floor.key"])
        assert db["floor.key"] == "value"

        keys = db.keys()
        assert len(keys) == 4
        print (keys)

        # banner("delete")
        # StopWatch.start("delete")
        # db.delete("floor.key")
        # StopWatch.stop("delete")
        # assert "floor.key" not in db
        # banner("db.data after delete")
        # print(db)

class g:

    def test_read_from_file(self):
        HEADING()
        global data
        print("DDD", data)
        self.filename = "tests/test.yaml"

        create_data_file(self.filename, data)

        banner(self.filename)
        content = readfile(self.filename)
        print(content)


        print(self.filename)
        db = YamlDB(filename=self.filename)
        db.save()

        banner("db.data")
        print(db)
        banner("value")
        print(db["floor.key"])

        assert db["floor.key"] == "value"

        banner("delete")
        StopWatch.start("delete")
        db.delete("floor.key")
        db.save()
        StopWatch.stop("delete")
        assert "floor.key" not in db
        banner("db.data after delete")
        print(db)

        banner(self.filename)
        content = readfile(self.filename)
        print (content)
    #

    def test_delete_variants(self):
        HEADING()
        self.filename = "tests/test.yaml"

        create_data_file(self.filename, data)


        db = YamlDB(filename=self.filename)
        db["floor.a"] = "value_a"
        db["floor.b"] = "value_b"
        db.save()

        banner("db values")
        print("BBBB", db)

        for key in ["floor.a", "floor.b"]:
            print(f"get   : {key}: {db[key]}")
            r = db.search("floor.a")
            print(f"search: {key}: {r}")



        db.delete("floor.a")

        db.save()
        print("AAAA", db.data)


        banner("db.data delete a")
        print(db)


        #
        # THIS DOES NOT YET WORK
        #
        # db.delete["floor"]
        # banner("db.data after delete")
        # print(db)

        #
        # THIS IS NOT YET TESTED
        #
        #try:
        #    db.delete["floor.key.nothing"]
        #except Exception as e:
        #    print (e)
        #    assert "could not be found" in str(e)
        #except TypeError:
        #    print ("UUU")

            # print (e)

        # banner ("AAA")
        # """
        #
        #
        # del db["floor"]
        # del db["floor.key"]
        # del ["floor.key.nothing"]
        # """

class aaa:

    def test_StopWatch(self):
        StopWatch.benchmark(sysinfo=False)
