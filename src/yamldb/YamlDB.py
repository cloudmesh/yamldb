"""from yamldb import YamlDB
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
from collections.abc import MutableMapping
from contextlib import suppress
from cloudmesh.common import dotdict


class YamlDB:
    """The YamlBD class uses a file based yaml file as its database backend."""

    def __init__(self, *, data=None, filename="yamldb.yml", backend=":file:"):
        """
        Initializes the YamlDB object.

        Args:
            data (dict, optional): The initial data to be stored in the database. Defaults to None.
            filename (str, optional): The name of the file to save the database. Defaults to "yamldb.yml".
            backend (str, optional): The backend storage type. Must be either ":file:" or ":memory:". Defaults to ":file:".

        Raises:
            ValueError: If the backend is not ":file:" or ":memory:".
            ValueError: If loading the database fails.

        """
        if backend not in [":file:", ":memory:"]:
            raise ValueError("backend must be :file: or :memory:")
        self.backend = backend
        self.filename = filename

        if os.path.exists(filename):
            if data is not None:
                self.data = data
                self.save(filename=filename)
            else:
                self.load(filename=filename)
        else:
            self._create_dir(filename)
            self.data = data if data is not None else {}
            self.save(filename=filename)

    def _create_dir(self, filename):
        """
        Create a directory for the given filename if it doesn't already exist.

        Args:
            filename (str): The path to the file.

        Raises:
            ValueError: If the directory cannot be created.

        """
        directory = os.path.dirname(filename)
        if directory is not None and directory != "":
            if not os.path.isdir(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except OSError as e:
                    raise ValueError(
                        f"YAMLDB: could not create directory={directory}"
                    ) from e

    def print_dictionary(self, dic, indent=0):
        """
        Prints the contents of a dictionary recursively.

        Parameters:
            dic (dict): The dictionary to be printed.
            indent (int): The number of tabs to be used for indentation.

        Returns:
            None
        """
        if len(dic) == 0:
            print("\t" * indent + "{}")
        for key, value in dic.items():
            print("\t" * indent + str(key))
            if isinstance(value, dict):
                self.print_dictionary(value, indent + 1)
            else:
                print("\t" * (indent + 1) + str(type(value)))

    def get_keys(self, d=None, keys_list=None, parent=""):
        """
        Recursively retrieves all keys in the YAML data.

        Args:
            d (dict, optional): The dictionary to traverse. Defaults to None.
            keys_list (list, optional): The list to store the keys. Defaults to None.
            parent (str, optional): The parent key. Defaults to "".

        Returns:
            list: A list of all keys in the YAML data.
        """
        if keys_list is None:
            keys_list = []
            keys_list = list(self.data.keys())
        if d is None:
            d = dict(self.data)
        for key, value in d.items():
            if isinstance(d[key], dict):
                self.get_keys(d[key], keys_list, parent=key)
            else:
                keys_list.append(f"{parent}.{key}")
        return keys_list

    def keys(self):
        """
        Returns a list of all the keys in the YamlDB object.
        """
        return self.get_keys()

    def __iter__(self):
        """Iterates over the first level of the keys.

        Returns:
            An iterator object that iterates over the keys in the first level of the data.
        """
        return iter(self.data)

    def __contains__(self, key):
        """Checks if the key is included in the db

        Args:
            key: The key to check for existence in the database.

        Returns:
            bool: True if the key is found in the database, False otherwise.
        """
        found = True
        try:
            self.__getitem__(key)
        except:
            found = False
        return found

    def clear(self):
        """Removes all data"""
        self.data.clear()
        self.flush()

    def load(self, filename=None):
        """Loads the data from the specified filename

        Args:
            filename (str): The path to the file to load the data from. If not provided, the default filename will be used.

        Returns:
            None

        """
        prefix = os.path.dirname(filename)
        if prefix is not None and prefix != "":
            if not os.path.exists(prefix):
                os.makedirs(prefix)

        name = filename or self.filename

        if os.path.exists(name):
            with open(name, "rb") as dbfile:
                self.data = yaml.safe_load(dbfile) or dict()

    def update(self, filename=None):
        """Inserts the data from the specified filename

        Args:
            filename (str): The path to the file containing the data to be inserted.

        Returns:
            None
        """
        # prefix = os.path.dirname(filename)
        # if not os.path.exists(prefix):
        #    os.makedirs(prefix)
        # the entry must have an id which is used as the name for the entry

        if os.path.exists(filename):
            with open(filename, "rb") as dbfile:
                data = yaml.safe_load(dbfile) or dict()
                id = data["id"] or "unknown"
                if id in ["unknown", "MISSING"]:
                    print(f"Error: id not found for {filename}")
                d = {id: data}
                self.data.update(d)

    def save(self, filename=None, indent=None):
        """
        Saves the data to the specified filename.

        Args:
            filename (str): The name of the file to save the data to. If not provided, the current filename will be used.
            indent (int): The number of spaces to use for indentation. If not provided, the default indentation will be used.

        Returns:
            None
        """
        name = filename or self.filename
        with open(name, "w") as stream:
            yaml.dump(self.data, stream, default_flow_style=False, indent=indent)

    def flush(self):
        """
        Saves the data to the file specified when the DB was loaded.

        Returns:
            None

        """
        if self.backend == ":file:":
            self.save()

    def close(self):
        """
        Close the DB without flushing the current content.

        Returns:
            None
        """
        self.flush()

    def dict(self):
        """Returns the dictionary representation of the data.

        Returns:
            dict: The dictionary representation of the data.
        """
        return self.data

    def yaml(self):
        """Returns the YAML representation of the data.

        Returns:
            str: The YAML string representation of the data.
        """
        return str(self.data)

    def __len__(self):
        """Return the number of elements in the top level.

        Returns:
            int: The number of elements in the top level.
        """
        len(self.data)

    def __setitem__(self, key, value):
        """Sets the item given at the key to value

        Args:
            key: The key to set the value for.
            value: The value to be set.

        Returns:
            None
        """
        self.set(key, value)

    def set(self, key, value):
        """A helper function for setting the default cloud in the config without
        a chain of `set()` calls.

        Usage:
            value = db.set('a.b.c.d', 'value')

        Args:
            key: A string representing the value's path in the config.
            value: value to be set.

        Raises:
            ValueError: If the key is not found in the yaml file or if there is an unknown error.
        """
        try:
            if value.lower() in ["true", "false"]:
                value = value.lower() == "true"
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
            raise ValueError(
                f"The key '{key}' could not be found in the yaml file '{self.filename}'"
            )
        except Exception as e:
            print(e)
            raise ValueError("unknown error")

        self.flush()

    def _delete_keys_from_dict(self, data, keys):
        """
        Recursively deletes keys from a nested dictionary.

        Args:
            data (dict): The dictionary from which keys will be deleted.
            keys (list): A list of keys to be deleted.

        Returns:
            None
        """
        for key in keys:
            with suppress(KeyError):
                print("DELETE", key, keys)
                del data[key]
        for value in data.values():
            if isinstance(value, MutableMapping):
                self._delete_keys_from_dict(value, keys)

    def delete(self, item):
        """Deletes an item from the dict. The key is . separated
        use it as follows get("a.b.c")

        Args:
            item (str): The key of the item to be deleted.

        Returns:
            None
        """
        try:
            if "." in item:
                keys = item.split(".")
                d = self.data
                for key in keys[:-1]:
                    d = d[key]
                    print("K", key, d)
                del_key = keys[-1]
                del d[del_key]
                self._delete_keys_from_dict(self.data, keys)
            else:
                del self.data[item]
                return
        except Exception as e:
            print(e)
            # raise ValueError("unknown error")

    def __delitem__(self, key):
        """
        Delete an item from the YamlDB instance.

        Args:
            key: The key of the item to delete.

        Returns:
            None
        """
        self.delete(key)

    def __getitem__(self, item):
        """gets an item from the dict. The key is . separated
        use it as follows get("a.b.c")

        Args:
            item (str): The key to retrieve from the dictionary.

        Returns:
            Any: The value associated with the given key.

        Raises:
            KeyError: If the key is not found in the yaml file.
            ValueError: If an unknown error occurs.
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
            raise KeyError(
                f"The key '{item}' could not be found in the yaml file '{self.filename}'"
            )
        except Exception as e:
            print(e)
            raise ValueError("unknown error")
        return element

    def get(self, key, default=None):
        """Gets the value based on the key.

        Args:
            key (str): A string representing the value's path in the config.
            default (Any, optional): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value associated with the key, or the default value if the key is not found.
        """
        try:
            return self.data[key]
        except KeyError:
            self[key] = default
            return default

    def search(self, query):
        """
        Searches the data using JMESPath query language.

        Args:
            query (str): The JMESPath query string.

        Returns:
            dict: A dictionary containing the search result.
        """
        return jmespath.search(query, self.data)

    def __str__(self):
        """Returns the YAML representation of the data as a string.

        Returns:
            str: The YAML representation of the data.
        """
        if self.data is None:
            return ""

        return yaml.dump(self.data, default_flow_style=False, indent=2)
