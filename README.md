YamlDB
======

[![GitHub Repo](https://img.shields.io/badge/github-repo-green.svg)](https://github.com/cloudmesh/yamldb)
[![image](https://img.shields.io/pypi/pyversions/yamldb.svg)](https://pypi.org/project/yamldb)
[![image](https://img.shields.io/pypi/v/yamldb.svg)](https://pypi.org/project/yamldb/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![General badge](https://img.shields.io/badge/Status-Production-<COLOR>.svg)](https://shields.io/)
[![GitHub issues](https://img.shields.io/github/issues/cloudmesh/yamldb.svg)](https://github.com/cloudmesh/yamldb/issues)
[![Contributors](https://img.shields.io/github/contributors/cloudmesh/yamldb.svg)](https://github.com/cloudmesh/yamldb/graphs/contributors)
[![General badge](https://img.shields.io/badge/Other-repos-<COLOR>.svg)](https://github.com/cloudmesh)


[![Linux](https://img.shields.io/badge/OS-Linux-orange.svg)](https://www.linux.org/)
[![macOS](https://img.shields.io/badge/OS-macOS-lightgrey.svg)](https://www.apple.com/macos)
[![Windows](https://img.shields.io/badge/OS-Windows-blue.svg)](https://www.microsoft.com/windows)


YamlDB is an easy to use file-based database using YAML as the format for the
data represented in the file. This makes it possible to quickly change and add
values in the file itself while it can then be loaded and used as a dict in your
application.

It has the ability to use a dot notations for the keys instead of nested brackets.
It also creates parents if they do not exist.

Note: you must be using python 3.8 or newer

```python
pip install yamldb

db = YamlDB(filename="data.yml")

db["a"] = "1"
db["b.c"] = "2"

d = db.get("a.b.c.d", default=3)

db.load()
  reloads the file
  
db.delete("b.c")
    deletes the key b.c
    to save the state you have to also call db.save()
    
db.save()
  saves the current db into the file

db.search("a.*.c")
   quries the db
   see: https://jmespath.org/tutorial.html
   
```

## Development and tests

The best way to contribute is with issues and pull requests. You will need to check out the development version such as

```bash
git clone https://github.com/cloudmesh/yamldb.git
cd yamldb
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Then you can run the a test with 

```bash
pytest -v --capture=no tests/test_config.py
```

## Alternatives

* jmespath: <https://jmespath.org/>
* TinyDB:   <https://tinydb.readthedocs.io/en/latest/index.html>
* nosqlite:  <https://github.com/shaunduncan/nosqlite>
* MongoDB:  This is quite a big package and we developed yamldb to replace it when mongo is not needed.

## Acknowledgments

Continued work was in part funded by the NSF
CyberTraining: CIC: CyberTraining for Students and Technologies
from Generation Z with the award numbers 1829704 and 2200409.
