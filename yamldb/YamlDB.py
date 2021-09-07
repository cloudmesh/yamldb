"""
from yamldb import YamlDB
from yamldb import Query

db = YamlDB('path/to/db.yaml')
user = Query()
db.insert({'name': 'Gregor', 'age': 111})
db.search("[?name=='Gregor']")

[{'name': 'Gregor', 'age': 111}]

"""
# pylint: disable=C0103,W0107,W0702
import os

import jmespath
import oyaml as yaml
from collections import MutableMapping
from contextlib import suppress

class YamlDB:
    """
    The YamlBD class uses a file based yaml file as its database backend.
    """

    def __init__(self, *, data=None, filename="yamldb.yml", backend=":file:"):
        """
        Initialized=s the data base, if data is not None it is
        used to initialize the DB.

        :param data:
        :type data:
        :param filename:
        :type filename:
        """
        if backend not in [":file:", ":memory:"]:
            raise ValueError("bakend must be :file: or :memory:")
        self.backend = backend
        self.filename = filename

        if os.path.exists(filename) and data is not None:
            self.data = data
            self.save(filename=filename)
        elif os.path.exists(filename) and data is None:
            self.load(filename=filename)
        elif not os.path.exists(filename) and data is not None:
            self.data = data
            self.save(filename=filename)
        elif not os.path.exists(filename) and data is None:
            self.data = {}
            self.save(filename=filename)
        else:
            raise ValueError("Load failed")

    def __iter__(self):
        """
        Itterates over the first level of the keys

        :return:
        :rtype:
        """
        return iter(self.data)

    def __contains__(self, key):
        """
        Checks if the key is included in the db

        :param key:
        :type key:
        :return:
        :rtype:
        """
        found = True
        try:
            self.__getitem__(key)
        except:
            found = False
        return found

    def clear(self):
        """
        Removes all data

        """
        self.data.clear()
        self.flush()

    def keys(self):
        return self.data.keys()

    def load(self, filename=None):
        """
        Loads the data from the specified filename

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        prefix = os.path.dirname(filename)
        if not os.path.exists(prefix):
            os.makedirs(prefix)

        name = filename or self.filename

        if os.path.exists(name):
            with open(name, 'rb') as dbfile:
                self.data = yaml.safe_load(dbfile) or dict()

    def save(self, filename=None):
        """
        saves the data to the specified filename

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        name = filename or self.filename
        with open(name, "w") as stream:
            yaml.dump(self.data, stream, default_flow_style=False)

    def flush(self):
        """
        saves the data to the file specified when the DB was loaded.

        :return:
        :rtype:
        """
        if self.backend == ":file:":
            self.save()

    def close(self):
        """
        Close the DB without flushing the current content
        """
        self.flush()

    def dict(self):
        """
        Retruns the dict of the data

        :return:
        :rtype:
        """
        return self.data

    def yaml(self):
        """
        Retruns the yaml of the data

        :return:
        :rtype:
        """
        return str(self.data)

    def __len__(self):
        """
        return the number of elements of the top level

        :return:
        :rtype:
        """
        len(self.data)

    def __setitem__(self, key, value):
        """
        Sets the item given at the key to value

        :param key:
        :type key:
        :param value:
        :type value:
        :return:
        :rtype:
        """
        self.set(key, value)

    def set(self, key, value):
        """
        A helper function for setting the default cloud in the config without
        a chain of `set()` calls.

        Usage:
            value = db.set('a.b.c.d', 'value')

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """
        try:
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
        except:
            pass

        try:
            if "." in key:
                keys = key.split(".")
                #
                # create parents
                #
                parents = keys[:-1]
                location = self.data
                for parent in parents:
                    if parent not in location:
                        location[parent] = {}
                    location = location[parent]
                #
                # create entry
                #
                location[keys[-1]] = value
            else:
                self.data[key] = value

        except KeyError:
            raise ValueError(f"The key '{key}' could not be found in the yaml file '{self.filename}'")
        except Exception as e:
            print(e)
            raise ValueError("unkown error")

        self.flush()

    def _delete_keys_from_dict(self, data, keys):
        # inspired from
        # https://stackoverflow.com/questions/3405715/elegant-way-to-remove-fields-from-nested-dictionaries
        for key in keys:
            with suppress(KeyError):
                del data[key]
        for value in data.values():
            if isinstance(value, MutableMapping):
                self._delete_keys_from_dict(value, keys)

    def delete(self, item):
        """
        Deletes an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                del self.data[item]
                return
            self._delete_keys_from_dict(self.data, keys)
        except Exception as e:
            print(e)
            raise ValueError("unkown error")

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, item):
        """
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                return self.data[item]
            element = self.data[keys[0]]
            for key in keys[1:]:
                element = element[key]
        except KeyError:
            raise KeyError(f"The key '{item}' could not be found in the yaml file '{self.filename}'")
        except Exception as e:
            print(e)
            raise ValueError("unkown error")
        return element

    def get(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param default:
        :param key: A string representing the value's path in the config.
        """
        try:
            return self.data[key]
        except KeyError:
            self[key] = default
            return default

    def search(self, query):
        """
        Searches the data with jmsepath see: https://jmespath.org/

        Example queries:
           "a.*.c"

           see: https://jmespath.org/tutorial.html

        :param query:
        :return: dict with the result
        """
        return jmespath.search(query, self.data)

    def __str__(self):
        """
        Returns the yaml as a string

        :return:
        :rtype:
        """
        if self.data is None:
            return ""

        return yaml.dump(self.data, default_flow_style=False, indent=2)
