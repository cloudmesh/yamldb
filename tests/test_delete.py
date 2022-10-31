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
        print(db.data)
        print(content)

        assert "floor.key" in db.data
        assert os.path.isfile(filename)

        StopWatch.start("delete")
        db.delete("floor.key")
        StopWatch.stop("delete")
        assert "floor.key" not in db

    def test_StopWatch(self):
        StopWatch.benchmark(sysinfo=False)
