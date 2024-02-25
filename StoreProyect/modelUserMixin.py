from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, lastname, username):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.username = username