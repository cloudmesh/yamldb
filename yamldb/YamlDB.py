"""
from yamldb import YamlDB
from yamldb import Query

db = YamlDB('path/to/db.yaml')
user = Query()
db.insert({'name': 'Gregor', 'age': 111})
db.search("[?name=='Gregor']")

[{'name': 'Gregor', 'age': 111}]

"""
import oyaml as yaml
import os
import jmespath


class YamlDB:

    def __init__(self, data=None, filename=None, backend=":file:"):
        """
        Initialized=s the data base, if data is not None it is
        used to initialize the DB.

        :param data:
        :type data:
        :param filename:
        :type filename:
        """
        self.backend = backend
        self.filename = filename
        if data is not None:
            self.data = data
        self.flush()

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
            self[key]
        except:
            found = False
        return found

    def clear(self):
        """
        Removes all data

        """
        self.data.clear()
        self.flush()

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
        with open(name, "wb") as stream:
            yaml.safe_dump(self.data, stream, default_flow_style=False)

    def flush(self):
        """
        saves the data to the file specified when the DB was loaded.

        :return:
        :rtype:
        """
        self.save()

    def close(self):
        """
        Close the DB without flushing the current content
        """
        pass

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

        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
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

        self.save()

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

    def __delitem__(self, item):
        """
        #
        # BUG THIS DOES NOT WORK
        #
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
            element = self.data
            print(keys)
            for key in keys:
                element = element[key]
            del element
        except KeyError:
            raise KeyError(f"The key '{item}' could not be found in the yaml file '{self.filename}'")
        except Exception as e:
            print(e)
            raise ValueError("unkown error")

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
        else:
            return yaml.dump(self.data, default_flow_style=False, indent=2)
