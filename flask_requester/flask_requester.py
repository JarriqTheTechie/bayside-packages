import os.path
import pprint
import re
import uuid
from typing import Any, Callable, Literal
from urllib import parse

import flask
import pendulum
from flask import request, flash, redirect, url_for, current_app
from flask.sessions import SessionMixin

from helpers import String


class FastInstantiateMeta(type):
    def __getattr__(self, attribute, *args, **kwargs):
        """This method is called between a Model and accessing a property. This is a quick and easy
        way to instantiate a class before the first method is called. This is to avoid needing
        to do this:

        User().where(..)

        and instead, with this class inherited as a meta class, we can do this:

        User.where(...)

        This class (potentially magically) instantiates the class even though we really didn't instantiate it.

        Args:
            attribute (string): The name of the attribute

        Returns:
            Model|mixed: An instantiated model's attribute
        """
        instantiated = self(*args, **kwargs)
        return getattr(instantiated, attribute)


class Session(object, metaclass=FastInstantiateMeta):
    def __init__(self):
        self.session = flask.session

    def get(self, key: str, default: Any = None) -> Any:
        return self.session.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.session[key] = value

    def put(self, key: str, value: Any) -> None:
        self.set(key, value)

    def has(self, key: str) -> bool:
        if self.get(key) is None:
            return False
        return True

    def missing(self, key: str) -> bool:
        return not self.has(key)

    def pull(self, key: str, default: Any = None) -> Any:
        if self.has(key):
            value = self.session[key]
            self.forget(key)
            return value
        return default

    def flush(self) -> None:
        self.session.clear()

    def forget(self, key: str|list) -> None:
        if type(key) == str:
            self.session.pop(key, None)
        elif type(key) == list:
            for x in key:
                self.session.pop(x, None)

    def increment(self, key: str, amount: int = 1) -> None:
        self.session[key] += amount

    def decrement(self, key: str, amount: int = 1) -> None:
        self.session[key] -= amount

    def flash(self, category: str, message: str) -> None:
        flask.flash(message, category)

    def all(self) -> SessionMixin:
        return self.session

    def old(self, key):
        old_data = self.get("old_")
        return old_data.get(key, None)



class requester(object, metaclass=FastInstantiateMeta):
    @classmethod
    def formDict(cls, url: str) -> dict:
        url: str = 'localhost?' + url
        return dict(parse.parse_qsl(parse.urlsplit(url).query))

    @classmethod
    def query(cls, key=None, default=None):
        data = cls.formDict(request.query_string.decode('utf-8'))
        if not key:
            return data
        return data.get(key, default)

    @classmethod
    def string(cls, string):
        return String.of(cls.input(string))

    @classmethod
    def all(cls, arrays: dict | None = None) -> dict:
        if arrays is None:
            arrays = []
        if request.method == 'GET':
            return cls.formDict(request.query_string.decode('utf-8'))
        elif request.method == 'POST' or request.method == 'PUT':
            if request.files and request.form:
                files = request.files.to_dict()
                form = request.form.to_dict()
                req = files.copy()
                req.update(form)
                for array in arrays:
                    key = array
                    data = request.form.getlist(f'{array}')
                    req[key] = data
                return req
            if request.files:
                files = request.files.to_dict()
                return files
            if request.form:
                form = request.form.to_dict()
                if len(arrays) > 0:
                    for array in arrays:
                        key = array
                        data = request.form.getlist(f'{array}')
                        form[key] = data
                return form

    @classmethod
    def input(cls, key: str, default: Any = None) -> Any:
        return cls.all().get(key, default)

    @classmethod
    def boolean(cls, key: str) -> bool:
        match cls.input(key):
            case 1:
                return True
            case "1":
                return True
            case True:
                return True
            case "true":
                return True
            case "on":
                return True
            case "yes":
                return True
            case _:
                return False

    @classmethod
    def date(cls, key, format=None, timezone=pendulum.now().timezone.name):
        date_from_request = cls.input(key)
        if not date_from_request:
            return date_from_request
        if not format:
            return pendulum.parse(date_from_request, tz=timezone)
        return pendulum.parse(date_from_request, tz=timezone).format(format)

    @classmethod
    def only(cls, list_of_keys: list) -> dict:
        if type(list_of_keys) == str:
            list_of_keys: list = [list_of_keys]
        array: dict = {}
        for item in list_of_keys:
            array[item] = cls.input(item)
        return array

    @classmethod
    def ignore(cls, ignore_keys: str | list) -> dict:
        if type(ignore_keys) == str:
            ignore_keys = [ignore_keys]

        all_keys = cls.all()
        for key in ignore_keys:
            all_keys.pop(key, None)
        return all_keys

    @classmethod
    def has(cls, key: str) -> bool:
        keys: list = []
        results: list = []
        if type(key) == str:
            keys = [key]
        elif type(key) == list:
            keys = key
        for key in keys:
            if key in cls.all():
                results.append(True)
            else:
                results.append(False)
        if False in results:
            return False
        else:
            return True

    @classmethod
    def when_has(cls, key: str, callback: callable, not_present_callback: callable) -> None:
        if cls.has(key):
            callback(cls.input(key))
        not_present_callback()

    @classmethod
    def filled(cls, key: str) -> bool:
        if cls.input(key) == "" or cls.input(key) is None:
            return False
        else:
            return True

    @classmethod
    def when_filled(cls, key: str, callback: callable, not_filled_callback: callable) -> None:
        if cls.filled(key):
            callback(cls.input(key))
        not_filled_callback()

    @classmethod
    def missing(cls, key: str) -> bool:
        if cls.input(key) is None:
            return True
        else:
            return False

    @classmethod
    def flash(cls) -> None:
        flash(cls.all())

    @classmethod
    def flash_only(cls, list_of_keys) -> None:
        flash(cls.only(list_of_keys))

    @classmethod
    def flash_ignore(cls, ignore_keys) -> None:
        flash(cls.ignore(ignore_keys))

    @classmethod
    def cookies(cls, key: str) -> Any:
        return request.cookies.get(key)

    @classmethod
    def merge(cls, array: dict) -> dict:
        return {**cls.all(), **array}

    @classmethod
    def merge_if_missing(cls, key: str, array: dict) -> dict:
        if cls.missing(key):
            return {**cls.all(), **array}
        else:
            return cls.all()

    # Files
    @classmethod
    def file(cls, key: str):
        file = cls.only(key)
        return file[key]

    @classmethod
    def hasFile(cls, key: str) -> bool:
        keys = cls.only(key)
        for x in keys:
            if keys[x].__dict__['filename'] == "":
                return False
            else:
                return True

    @classmethod
    def store(cls, key: str, prefix: str = "", suffix: str = "", prefix_separator: str = "", suffix_separator: str = "",
              keep_name: bool = False) -> str:
        extension: str = os.path.splitext(cls.file(key).__dict__['filename'])[1][1:].strip()
        if keep_name is True:
            with cls.file(key).__dict__['stream'] as f:
                file_guts: bytes = f.read()
            with open(r'UPLOADS\\' + f'{prefix}{prefix_separator}{cls.file(key).__dict__["filename"]}', 'wb') as output:
                output.write(file_guts)
            return cls.file(key).__dict__['filename']
        cls.file(key).__dict__[
            'filename'] = f"{prefix}{prefix_separator}{str(uuid.uuid4())}{suffix_separator}{suffix}" + "." + extension
        with cls.file(key).__dict__['stream'] as f:
            file_guts: bytes = f.read()
        with open(r'UPLOADS\\' + f'{cls.file(key).__dict__["filename"]}', 'wb') as output:
            output.write(file_guts)
        return cls.file(key).__dict__['filename']

    @classmethod
    def upload_multiple(cls, key: str, keep_name: bool = False):
        saved_file_path_list: list = []
        files: list = request.files.getlist(f'{key}')
        for file in files:
            extension: str = os.path.splitext(file.filename)[1][1:].strip()
            if keep_name is False:
                file.filename = str(uuid.uuid4()) + "." + extension
            with file.stream as f:
                file_guts: bytes = f.read()
            with open(r'UPLOADS\\' + f'{file.filename}', 'wb') as output:
                output.write(file_guts)
            saved_file_path_list.append(file.filename)
        return saved_file_path_list

    @classmethod
    def session(cls, *args) -> Session:
        return Session(*args)

    def __getattr__(self, name):
        data = self.input(name)
        if data:
            return data
        data = self.query(name)
        if data:
            return data
        return None



class redirector(object, metaclass=FastInstantiateMeta):
    @classmethod
    def to(self, path_or_route: str):
        """
        Instantiate a new String object.
        :param string:
        :return:
        """
        obj = self()
        obj.path_or_route = path_or_route
        return obj

    def route(self, *args, **kwargs):
        if not self.path_or_route:
            return self
        if "/" in self.path_or_route:
            return redirect(self.path_or_route)
        else:
            return redirect(url_for(self.path_or_route))

    def away(self):
        if "https" in self.path_or_route or "http" in self.path_or_route:
            return redirect(self.path_or_route)
        return redirect(f"https://{self.path_or_route}")

    def with_(self, category: str, message: Any):

        flash(message=message, category=category)
        return self.route()

    def back(self):
        return redirect(request.referrer)

    def back_with_errors(self, validator):
        requester.session().flash("errors", validator.errors())
        requester.session().flash("old_", validator.old())
        return self.back()

    def back_with_input(self):
        requester.session().flash("old_", requester.all())
        return self.back()








