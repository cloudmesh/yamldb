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


```
pip install yamldb

db = YamlDB(filename="data.yml")

db["a"] = "1"
db["b.c"] = "2"

d = db.get("a.b.c.d", default=3)

db.load()
  reloads the file
  
db.save()
  saves the current db into the file

db.search("a.*.c")
   quries the db
   see: https://jmespath.org/tutorial.html
```

## Aalternatives

* jmsepath: https://jmespath.org/
* TinyDB: https://tinydb.readthedocs.io/en/latest/index.html
* nsqlite: https://github.com/shaunduncan/nosqlite
* MongoDB:
* Codernity: ? http://labs.codernity.com/
