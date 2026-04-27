"""from yamldb import YamlDB
from yamldb import Query

db = YamlDB('path/to/db.yaml')
user = Query()
db.insert({'name': 'Gregor', 'age': 111})
db.search("[?name=='Gregor']")

[{'name': 'Gregor', 'age': 111}]

"""
# pylint: disable=C0103,W0107,W0702
from pathlib import Path

import os
import tempfile
import time
import copy
import portalocker
import msgpack
from contextlib import suppress, contextmanager
from typing import Any, Dict, List, Optional, Union, Generator, Callable
import jmespath
from ruamel.yaml import YAML
from collections.abc import MutableMapping
from .backends import FileBackend, BinaryBackend, EncryptedBackend

class MockConsole:
    def print(self, msg): print(msg)
    def error(self, msg): print(f"ERROR: {msg}")
    def banner(self, title, subtitle=""): print(f"=== {title} ===\n{subtitle}")
    def table(self, headers, data, title=""): print(f"{title}\n{headers}\n{data}")

console = MockConsole()


class YamlDB:
    """The YamlBD class uses a file based yaml file as its database backend."""

    data: Dict[Any, Any]
    filename: str
    backend: str
    _in_transaction: bool
    _lock_file: Path
    _lock_handle: Any = None
    _set_calls: int = 0
    _save_calls: int = 0

    def __init__(
        self, *, data: Optional[Any] = None, filename: str = "yamldb.yml", backend: str = ":file:", auto_flush: bool = True, password: Optional[str] = None
    ) -> None:
        self._initializing = True
        self._yaml = YAML(typ='rt')
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=4, offset=2)
        self.auto_flush = auto_flush
        self._dirty = False
        self._set_calls = 0
        self._save_calls = 0
        
        if backend not in [":file:", ":memory:", ":binary:", ":encrypt:"]:
            raise ValueError("backend must be :file:, :memory:, :binary:, or :encrypt:")
        
        if backend == ":encrypt:" and not password:
            raise ValueError("password is required for :encrypt: backend")
        
        self.backend = backend
        self.password = password
        self.filename = filename
        self._in_transaction = False
        self._lock_file = Path(f"{filename}.lock")
        
        # Initialize Backend Strategy
        if backend == ":file:":
            self._backend = FileBackend()
        elif backend == ":binary:":
            self._backend = BinaryBackend()
        elif backend == ":encrypt:":
            self._backend = EncryptedBackend(password)
        else: # :memory:
            self._backend = None

        self.data = {}

        path = Path(filename)
        if path.exists():
            if data is not None:
                self.data = data
                self.save(filename=filename)
            else:
                self.load(filename=filename)
        else:
            self._create_dir(filename)
            if data is not None:
                self.data = data
            else:
                self.data = {}
            
            if self._backend:
                self.save(filename=filename)
        self._initializing = False

    def _acquire_lock(self, timeout: float = 5.0) -> bool:
        """Acquires a file lock to prevent concurrent access."""
        if self.backend == ":memory:":
            return True
        
        try:
            # Open the lock file and apply an exclusive lock
            self._lock_handle = open(self._lock_file, "wb")
            portalocker.lock(self._lock_handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
            return True
        except (portalocker.exceptions.LockException, IOError):
            # If lock fails, we can implement a retry loop with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    self._lock_handle = open(self._lock_file, "wb")
                    portalocker.lock(self._lock_handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
                    return True
                except (portalocker.exceptions.LockException, IOError):
                    time.sleep(0.1)
            raise RuntimeError(f"Timeout acquiring lock on {self._lock_file}")

    def _release_lock(self) -> None:
        """Releases the file lock."""
        if self.backend == ":memory:" or self._lock_handle is None:
            return
        try:
            portalocker.unlock(self._lock_handle)
            self._lock_handle.close()
            # Clean up the lock file to satisfy tests and keep filesystem clean
            with suppress(FileNotFoundError):
                self._lock_file.unlink()
        finally:
            self._lock_handle = None

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """
        Context manager for database transactions.
        
        Changes are kept in memory and only flushed to disk on successful exit.
        If an exception occurs, changes are rolled back.
        """
        self._in_transaction = True
        # Use deepcopy to ensure nested dictionaries are also backed up
        backup_data = copy.deepcopy(self.data) if self.data else {}
        try:
            yield
            # Use save() directly because flush() skips saving when _in_transaction is True
            if self.backend == ":file:":
                self.save()
        except Exception:
            self.data = backup_data
            raise
        finally:
            self._in_transaction = False

    def _create_dir(self, filename: str) -> None:
        """
        Create a directory for the given filename if it doesn't already exist.

        Args:
            filename (str): The path to the file.

        Raises:
            ValueError: If the directory cannot be created.

        """
        directory = Path(filename).parent
        if directory != Path("."):
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ValueError(
                    f"YAMLDB: could not create directory={directory}"
                ) from e

    def print_dictionary(self, dic: Dict[Any, Any], indent: int = 0) -> None:
        """
        Prints the contents of a dictionary. 
        Uses a table for the top level and recursive printing for nested dicts.
        """
        if not dic:
            console.print("{}")
            return

        if indent == 0:
            # Add a banner for the database overview
            console.banner("Database Overview", f"File: {self.filename}")

            # Use a table for the top-level overview
            data = [(k, v if not isinstance(v, dict) else "dict") for k, v in dic.items()]
            console.table(["Key", "Value"], data, title="Database Contents")
            
            # Then print details for nested dicts
            for k, v in dic.items():
                if isinstance(v, dict):
                    console.print(f"\n[bold blue]Details for {k}:[/bold blue]")
                    self.print_dictionary(v, indent=1)
        else:
            # Recursive indented printing for nested structures
            for key, value in dic.items():
                console.print("\t" * indent + str(key))
                if isinstance(value, dict):
                    self.print_dictionary(value, indent + 1)
                else:
                    console.print("\t" * (indent + 1) + str(value))

    def get_keys(
        self, d: Optional[Dict[Any, Any]] = None, keys_list: Optional[List[str]] = None, parent: str = ""
    ) -> List[str]:
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

    def keys(self) -> List[str]:
        """
        Returns a list of all the keys in the YamlDB object.
        """
        return self.get_keys()

    def __iter__(self) -> Generator[Any, None, None]:
        """Iterates over the first level of the keys.

        Returns:
            An iterator object that iterates over the keys in the first level of the data.
        """
        return iter(self.data)

    def __contains__(self, key: Any) -> bool:
        """Checks if the key is included in the db

        Args:
            key: The key to check for existence in the database.

        Returns:
            bool: True if the key is found in the database, False otherwise.
        """
        try:
            self.__getitem__(key)
            return True
        except (KeyError, ValueError):
            return False

    def clear(self) -> None:
        """Removes all data"""
        self.data.clear()
        self._dirty = True
        self.flush()

    def load(self, filename: Optional[str] = None, _loaded_files: Optional[set] = None) -> None:
        """Loads the data from the specified filename."""
        is_top_level = _loaded_files is None
        if _loaded_files is None:
            _loaded_files = set()

        name = filename or self.filename
        path = Path(name).resolve()
        
        if path in _loaded_files:
            return
        _loaded_files.add(path)

        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            self._acquire_lock()
            try:
                if self._backend:
                    self.data = self._backend.load(str(path))
                else:
                    self.data = {}
                
                # Handle #load directives for FileBackend specifically
                if self.backend == ":file:":
                    with open(path, "r") as dbfile:
                        lines = dbfile.readlines()
                    for line in lines:
                        line = line.strip()
                        if line.startswith("#load"):
                            content = line[5:].strip()
                            if content.startswith(":"):
                                content = content[1:].strip()
                            load_path = (path.parent / content).resolve()
                            loaded_data = self._load_yaml_file(load_path, _loaded_files)
                            if loaded_data:
                                if self.data is None: self.data = {}
                                self.data.update(loaded_data)
            finally:
                self._release_lock()
        
        if is_top_level:
            self._resolve_variables()
            self._dirty = False

    def _load_yaml_file(self, path: Path, loaded_files: set) -> Dict[Any, Any]:
        """Helper to load a YAML file and its #load directives without updating self.data directly."""
        if path in loaded_files:
            return {}
        loaded_files.add(path)

        if not path.exists():
            return {}

        try:
            with open(path, "r") as dbfile:
                lines = dbfile.readlines()
            
            data = {}
            for line in lines:
                line = line.strip()
                if line.startswith("#load"):
                    # Support both "#load path" and "#load: path"
                    content = line[5:].strip()
                    if content.startswith(":"):
                        content = content[1:].strip()
                    load_file = content
                    load_path = (path.parent / load_file).resolve()
                    loaded_data = self._load_yaml_file(load_path, loaded_files)
                    data.update(loaded_data)
            
            with open(path, "r") as dbfile:
                file_data = self._yaml.load(dbfile) or {}
                data.update(file_data)
            return data
        except Exception as e:
            console.error(f"Error loading file {path}: {e}")
            return {}



    def _resolve_variables(self) -> None:
        """Resolves variables in the form of {a.b} in the data."""
        def resolve_value(val: Any) -> Any:
            if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                var_path = val[1:-1]
                try:
                    return self.__getitem__(var_path)
                except (KeyError, ValueError):
                    return val
            elif isinstance(val, MutableMapping):
                for k, v in val.items():
                    val[k] = resolve_value(v)
                return val
            elif isinstance(val, list):
                for i in range(len(val)):
                    val[i] = resolve_value(val[i])
                return val
            return val

        if self.data:
            resolve_value(self.data)

    def update(self, filename: Optional[str] = None) -> None:
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
            with open(filename, "r") as dbfile:
                data = self._yaml.load(dbfile) or {}
                id = data["id"] or "unknown"
                if id in ["unknown", "MISSING"]:
                    console.error(f"id not found for {filename}")
                d = {id: data}
                self.data.update(d)

    def save(self, filename: Optional[str] = None, indent: Optional[int] = None) -> None:
        """Saves the data to the specified filename atomically."""
        name = filename or self.filename
        
        self._acquire_lock()
        try:
            if self._backend:
                self._backend.save(name, self.data)
            
            self._dirty = False
            if not getattr(self, '_initializing', False):
                self._save_calls += 1
        finally:
            self._release_lock()

    def flush(self) -> None:
        """
        Saves the data to the file specified when the DB was loaded.

        Returns:
            None

        """
        if self.backend != ":memory:" and not self._in_transaction:
            if self.auto_flush and self._dirty:
                self.save()

    def close(self) -> None:
        """
        Close the DB without flushing the current content.

        Returns:
            None
        """
        self.flush()

    def dict(self) -> Dict[Any, Any]:
        """Returns the dictionary representation of the data.

        Returns:
            dict: The dictionary representation of the data.
        """
        return self.data

    def yaml(self) -> str:
        """Returns the YAML representation of the data.

        Returns:
            str: The YAML string representation of the data.
        """
        import io
        stream = io.StringIO()
        self._yaml.dump(self.data, stream)
        return stream.getvalue()

    def __len__(self) -> int:
        """Return the number of elements in the top level.

        Returns:
            int: The number of elements in the top level.
        """
        return len(self.data)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sets the item given at the key to value

        Args:
            key: The key to set the value for.
            value: The value to be set.

        Returns:
            None
        """
        self.set(key, value)

    def set(self, key: str, value: Any, cast: Optional[Callable] = None) -> None:
        """A helper function for setting the default cloud in the config without
        a chain of `set()` calls.

        Usage:
            value = db.set('a.b.c.d', 'value', cast=int)

        Args:
            key: A string representing the value's path in the config.
            value: value to be set.
            cast (Callable, optional): A function to cast the value to a specific type.

        Raises:
            ValueError: If the key is not found in the yaml file or if there is an unknown error.
        """
        if cast:
            try:
                value = cast(value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Could not cast value '{value}' using {cast}: {e}")

        try:
            if isinstance(value, str) and value.lower() in ["true", "false"]:
                value = value.lower() == "true"
        except (AttributeError, ValueError):
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
                        if self.backend == ":file:":
                            import io
                            location[parent] = self._yaml.load(io.StringIO("")) or {}
                        else:
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
        except (KeyError, TypeError) as e:
            console.error(f"Error setting key {key}: {e}")
            raise ValueError(f"Could not set key {key}: {e}")

        self._set_calls += 1
        self._dirty = True
        if not self._in_transaction:
            self.flush()

    def _delete_keys_from_dict(self, data: Dict[Any, Any], keys: List[str]) -> None:
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
                del data[key]
        for value in data.values():
            if isinstance(value, MutableMapping):
                self._delete_keys_from_dict(value, keys)

    def delete(self, item: str) -> None:
        """Deletes an item from the dict. The key is . separated
        use it as follows get("a.b.c")

        Args:
            item (str): The key of the item to be deleted.

        Returns:
            None
        """
        try:
            self._dirty = True
            if "." in item:
                keys = item.split(".")
                d = self.data
                for key in keys[:-1]:
                    d = d[key]
                del_key = keys[-1]
                del d[del_key]
            else:
                del self.data[item]
                return
        except (KeyError, TypeError) as e:
            console.error(f"Error deleting item {item}: {e}")
            # raise ValueError("unknown error")

    def __delitem__(self, key: str) -> None:
        """
        Delete an item from the YamlDB instance.

        Args:
            key: The key of the item to delete.

        Returns:
            None
        """
        self.delete(key)

    def __getitem__(self, item: str) -> Any:
        """gets an item from the dict. The key is . separated
        use it as follows get("a.b.c")
        Supports wildcards (e.g., "a.*.b") which return a list of matches.

        Args:
            item (str): The key to retrieve from the dictionary.

        Returns:
            Any: The value associated with the given key, or a list of values if a wildcard is used.

        Raises:
            KeyError: If the key is not found in the yaml file.
            ValueError: If an unknown error occurs.
        """
        if "*" in item:
            res = self.search(item)
            # Flatten result if it's a list of lists to maintain compatibility with tests
            if isinstance(res, list) and res and isinstance(res[0], list):
                flattened = []
                for sublist in res:
                    flattened.extend(sublist)
                return flattened
            return res

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
        except (KeyError, TypeError) as e:
            console.error(f"Error retrieving item {item}: {e}")
            raise ValueError(f"Error retrieving item {item}: {e}")
        return element

    def get(self, key: str, default: Any = None) -> Any:
        """Gets the value based on the key.

        Args:
            key (str): A string representing the value's path in the config.
            default (Any, optional): The default value to return if the key is not found. Defaults to None.

        Returns:
            Any: The value associated with the given key, or the default value if not found.
        """
        try:
            return self.__getitem__(key)
        except (KeyError, ValueError):
            return default

    def get_as(self, key: str, cast: Callable, default: Any = None) -> Any:
        """Gets the value based on the key and casts it to the specified type.

        Args:
            key (str): A string representing the value's path in the config.
            cast (Callable): A function to cast the value to a specific type.
            default (Any, optional): The default value to return if not found or casting fails. Defaults to None.

        Returns:
            Any: The casted value, or the default value if not found or casting fails.
        """
        val = self.get(key, default)
        if val is None:
            return default
        try:
            return cast(val)
        except (ValueError, TypeError):
            return default

    def search(self, query: str) -> Any:
        """
        Searches the data using JMESPath query language.

        Args:
            query (str): The JMESPath query string.

        Returns:
            dict: A dictionary containing the search result.
        """
        return jmespath.search(query, self.data)

    def items_recursive(self, d: Optional[Dict[Any, Any]] = None, parent: str = "") -> Generator[tuple[str, Any], None, None]:
        """
        Recursively yields all leaf nodes in the database as (dot_notation_key, value) pairs.

        Args:
            d (dict, optional): The dictionary to traverse. Defaults to None.
            parent (str): The parent key path. Defaults to "".

        Yields:
            tuple: A tuple containing the full dot-notation key and the value.
        """
        if d is None:
            d = self.data

        for key, value in d.items():
            full_key = f"{parent}.{key}" if parent else key
            if isinstance(value, MutableMapping):
                yield from self.items_recursive(value, full_key)
            else:
                yield (full_key, value)

    def find_all(self, value: Any) -> List[str]:
        """
        Finds all keys that have the specified value.

        Args:
            value (Any): The value to search for.

        Returns:
            list: A list of dot-notation keys that match the value.
        """
        return [key for key, val in self.items_recursive() if val == value]

    def filter(self, predicate: Callable[[Any], bool]) -> List[str]:
        """
        Finds all keys where the value satisfies the given predicate.

        Args:
            predicate (Callable): A function that returns True for values to include.

        Returns:
            list: A list of dot-notation keys that satisfy the predicate.
        """
        return [key for key, val in self.items_recursive() if predicate(val)]

    def update_many(self, data_dict: Dict[str, Any]) -> None:
        """
        Updates multiple keys in a single transaction.

        Args:
            data_dict (dict): A dictionary of dot-notation keys and their new values.
        """
        with self.transaction():
            for key, value in data_dict.items():
                self.set(key, value)

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about the database write efficiency.

        Returns:
            dict: A dictionary containing set_calls, save_calls, and efficiency.
        """
        efficiency = 0.0
        if self._set_calls > 0:
            efficiency = 1.0 - (self._save_calls / self._set_calls)
        
        return {
            "set_calls": self._set_calls,
            "save_calls": self._save_calls,
            "write_efficiency": f"{efficiency:.2%}"
        }

    def convert_to_yaml(self, filename: str) -> None:
        """
        Exports the current database state to a human-readable YAML file.
        Useful for debugging binary databases.

        Args:
            filename (str): The path to the output YAML file.
        """
        path = Path(filename)
        self._create_dir(filename)
        with open(path, "w") as f:
            self._yaml.dump(self.data, f)

    def count(self, query: str) -> int:
        """
        Counts the number of items matching the JMESPath query.

        Args:
            query (str): The JMESPath query string.

        Returns:
            int: The number of matching items.
        """
        res = self.search(query)
        if isinstance(res, list):
            return len(res)
        return 1 if res is not None else 0

    def upsert(self, key: str, value: Any, cast: Optional[Callable] = None) -> bool:
        """
        Updates an existing key or inserts a new one.
        
        Returns:
            bool: True if a new key was inserted, False if an existing key was updated.
        """
        exists = key in self
        self.set(key, value, cast=cast)
        return not exists

    def merge(self, data: Union[Dict, str]) -> None:
        """
        Deep merges another dictionary or YAML file into the current database.

        Args:
            data (Union[Dict, str]): A dictionary to merge, or a path to a YAML file.
        """
        if isinstance(data, str):
            # Load from file
            temp_db = YamlDB(filename=data, backend=":file:")
            merge_data = temp_db.data
        else:
            merge_data = data

        self._deep_merge(merge_data, self.data)
        self._dirty = True
        self.flush()

    def _deep_merge(self, source: Dict, destination: Dict) -> None:
        """Recursively merges source into destination."""
        for key, value in source.items():
            if isinstance(value, MutableMapping) and key in destination and isinstance(destination[key], MutableMapping):
                self._deep_merge(value, destination[key])
            else:
                destination[key] = value

    def __str__(self) -> str:
        """Returns the YAML representation of the data as a string.

        Returns:
            str: The YAML string representation of the data.
        """
        if self.data is None:
            return ""

        return self.yaml()
