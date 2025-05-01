import json
from pathlib import Path
from flask import session

USER_DATA_PATH = Path("app/data/users.json")

class User:
    def __init__(self, username, password, role="student"):
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

    @staticmethod
    def from_dict(data):
        return User(
            username=data["username"],
            password=data["password"],
            role=data.get("role", "student")
        )

    def login(self):
        """
        Gọi AuthenticationService để đăng nhập.
        Trả về True nếu thành công, ngược lại False.
        """
        user = AuthenticationService.authenticateUser(self.username, self.password)
        if user:
            session["user"] = user.to_dict()
            return True
        return False

    def logout(self):
        """
        Gọi AuthenticationService để đăng xuất.
        """
        AuthenticationService.logoutUser(self)


# -------------------------------
# Lớp AuthenticationService
# -------------------------------
class AuthenticationService:
    @staticmethod
    def load_users():
        if USER_DATA_PATH.exists():
            with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {u["username"]: User.from_dict(u) for u in data}
        return {}

    @staticmethod
    def authenticateUser(username, password):
        """
        Kiểm tra thông tin đăng nhập.
        Trả về User nếu hợp lệ, ngược lại trả về None.
        """
        users = AuthenticationService.load_users()
        user = users.get(username)
        if user and user.password == password:
            return user
        return None

    @staticmethod
    def logoutUser(user):
        """
        Xóa session hiện tại, kết thúc phiên đăng nhập.
        """
        session.pop("user", None)
