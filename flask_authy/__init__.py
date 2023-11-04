from dotenv import load_dotenv
import os
try:
    from flask import session
    from flask.wrappers import Request
except ImportError:
    raise ImportError("Please ensure that flask is installed")

load_dotenv()

try:
    user_model_name = os.getenv("AuthUserModel") or "PrimacyUser"
    exec(f"from application.models.{user_model_name} import {user_model_name}")
except ImportError:
    raise NotImplementedError("Please ensure that User model exists in application/models directory")

try:
    from masoniteorm.models import Model
except ImportError:
    raise NotImplementedError("Please ensure that Masonite ORM is installed")


class Authenticatable:
    def __eq__(self, other):
        user_model_name = os.getenv("AuthUserModel") or "PrimacyUser"
        try:
            exec(f"from application.models.{user_model_name} import {user_model_name}")
            print("UGH RUNNING AUTHENTICATABLE")
        except ImportError:
            raise NotImplementedError("Please ensure that User model exists in application/models directory")
        user_model_class = globals().get(user_model_name)
        if isinstance(other, user_model_class):
            return self.__attributes__ == other.__attributes__


class Auth:
    @classmethod
    def user(cls):
        user_model_name = os.getenv("AuthUserModel") or "PrimacyUser"
        try:
            exec(f"from application.models.{user_model_name} import {user_model_name}")
        except ImportError:
            raise NotImplementedError("Please ensure that User model exists in application/models directory")
        username_field = os.getenv("AuthUsernameField") or "UserId"
        exec(f"flask_authy_user = {user_model_name}.where('{username_field}', session['username']).first()", globals())
        flask_authy_user = globals().get("flask_authy_user")
        if flask_authy_user:
            return flask_authy_user
        else:
            return None

    @classmethod
    def id(cls):
        return cls.user().id

    @classmethod
    def attempt(cls, username, password=None, condition=None):
        username_field = os.getenv("AuthUsernameField") or "UserId"
        password_field = os.getenv("AuthPasswordField") or "password"
        if password:
            # Todo: Add login driver. Should lookup from config
            raise NotImplementedError("Attempt with email and password not implemented as yet.")

        try:
            from application.models.User import User
            if isinstance(username, str):
                user = User.where(username_field, username).first()
            else:
                user_id = username
                user = User.find(user_id)
            session["username"] = user[username_field]

            return cls.user()
        except ImportError:
            return None

    @classmethod
    def login(cls, user):
        username_field = os.getenv("AuthUsernameField") or "UserId"
        cls.attempt(user[username_field])

    @classmethod
    def login_using_id(cls, id):
        pass

    @classmethod
    def check(cls):
        if cls.user():
            return True
        return None

    @classmethod
    def logout(cls):
        session.clear()


Request.user = Auth().user
