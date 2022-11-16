YamlDB
======

![https://img.shields.io/github/license/cloudmesh/yamldb](https://img.shields.io/github/license/cloudmesh/yamldb)

[![image](https://img.shields.io/travis/TankerHQ/yamldb.svg?branch=main)](https://travis-ci.org/TankerHQ/cloudmesn-db)

[![image](https://img.shields.io/pypi/pyversions/yamldb.svg)](https://pypi.org/project/yamldb)

[![image](https://img.shields.io/pypi/v/yamldb.svg)](https://pypi.org/project/yamldb/)


YamlDB is an easy to use file based database using yaml as the format for the
data represented in the file. This makes it possible to quickly change and add
values in the file itself while it can than be loaded and used as dict in your
application.

It had the ability to use dot notations for the keys instead of nested brackets.
It als creates parents if they do nt exist

Note: you must be using python 3.8 or newer

```
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

## Aalternatives

* jmsepath: https://jmespath.org/
* TinyDB: https://tinydb.readthedocs.io/en/latest/index.html
* nsqlite: https://github.com/shaunduncan/nosqlite
* MongoDB:

## Acknowledgments

Continued work was in part funded by the NSF
CyberTraining: CIC: CyberTraining for Students and Technologies
from Generation Z with the awadrd numbers 1829704 and 2200409.
