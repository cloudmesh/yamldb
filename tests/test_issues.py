###############################################################
# pytest -v --capture=no tests/test_issues.py
# pytest -v  tests/test_issues.py
# pytest -v --capture=no  tests/test_issues..py::test_issues::<METHODNAME>
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


@pytest.mark.incremental
class TestConfig:
    def test_issue_6_from_data(self):
        HEADING()
        data = YamlDB(filename="tmp_a.yaml", data={"bot": {"lang": "a"}})
        print(data)

        bot_lang = data["bot.lang"]
        print("Result:", bot_lang)
        assert bot_lang == "a"

    def test_issue_6_from_value(self):
        HEADING()
        data = YamlDB(filename="tmp_b.yaml")
        # data["bot.lang"] = "a"
        # print(data)
        # bot_lang = data["bot.lang"]
        # print("Result:", bot_lang)

    # def test_issue_6_from_case(self):
    #     locals = YamlDB(filename="tmp_locals.yaml")
    #     data = YamlDB(filename="tmp_data.yaml")
    #     data["bot.lang"] = "a"
    #     bot_lang = data["bot.lang"]
    #     assert bot_lang == "a"
