###############################################################
# pytest -v --capture=no tests/test_delete.py
# pytest -v  tests/test_delete.py
# pytest -v --capture=no  tests/test_delete..py::test_delete::<METHODNAME>
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
from cloudmesh.common.util import banner

if os_is_windows:
    filename = "~/.cloudmesh/cloudmesh.yaml"
else:
    filename = "/tmp/cloudmesh.yaml"

filename = path_expand(filename)

data = {
    "floor": {
        "key": "value"
    }
}

@pytest.mark.incremental
class TestConfig:

    def test_delete(self):
        HEADING()
        StopWatch.start("init")
        db = YamlDB(data=data, filename=filename)
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
        assert os.path.isfile(filename)

        banner("delete")
        StopWatch.start("delete")
        db.delete("floor.key")
        StopWatch.stop("delete")
        assert "floor.key" not in db
        banner("db.data after delete")
        print(db)


    def test_StopWatch(self):
        StopWatch.benchmark(sysinfo=False)
