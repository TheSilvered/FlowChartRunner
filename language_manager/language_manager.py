import os.path
from asset_manager import get_language


class LanguageError(Exception):
    pass


class MissingKey(str):
    def __getattr__(self, item):
        return MissingKey(self + "." + item)

    def __repr__(self):
        return f"MissingKey({super().__repr__()})"


class LanguageCategory:
    def __init__(self, path):
        self._values = {}
        self._path = path

    def __setattr__(self, key, value):
        if isinstance(key, str) and key.startswith("_"):
            self.__dict__[key] = value
            return
        elif key in self._values:
            raise LanguageError(f"setting duplicate {key} for {self._path}")
        self._values[key] = value

    def __getattr__(self, key):
        return super().__getattribute__("_values").get(key, MissingKey(super().__getattribute__("_path") + "." + key))

    def __getitem__(self, item):
        if isinstance(item, str) and item.startswith("_"):
            return self.__dict__[item]
        if "." in item:
            items = item.split(".")
            curr_item = self
            for item in items:
                curr_item = curr_item[item]
            return curr_item
        else:
            return self.__getattr__(item)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __repr__(self):
        return f"LanguageCategory({super().__getattribute__('_values')})"


class Language:
    def __init__(self, language_file):
        path = get_language(language_file)
        self.__values = LanguageCategory(os.path.basename(os.path.splitext(path)[0]))

        with open(path, encoding="UTF-8") as f:
            values = f.read().replace("\r\n", "\n").replace("\r", "\n").split("\n")

        for value in values:
            value = value.strip()
            if not value or value.startswith("#"):
                continue
            self.__load_value(value)

    def __load_value(self, value):
        keys, value = value.split("=", maxsplit=1)
        keys = keys.split(".")
        self.__add_category_entry(keys, value)

    def __add_category_entry(self, keys, value):
        path = self.__values["_path"]
        category = self.__values
        for key in keys[:-1]:
            path += "." + key
            sub_category = category[key]
            if isinstance(sub_category, LanguageCategory):
                category = sub_category
                continue
            elif isinstance(sub_category, MissingKey):
                sub_category = LanguageCategory(path)
                category[key] = sub_category
                category = sub_category
                continue
            else:
                raise LanguageError("trying to access a subclass that is also a value")

        category[keys[-1]] = value

    def __getattr__(self, item):
        return self.__values[item]

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        return f"Language({self.__values})"
