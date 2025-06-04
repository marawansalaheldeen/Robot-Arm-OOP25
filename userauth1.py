import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import hashlib
import secrets
from cryptography.fernet import Fernet


class User:
    def __init__(self, username, password, public_key=None, private_key=None):
        self._username = username
        self._password_hash = self._hash_password(password)
        self._public_key = public_key
        self._private_key = private_key

    @property
    def username(self):
        return self._username

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def _hash_password(self, password):
        salt = secrets.token_hex(16)
        hash_ = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hash_}"

    def verify_password(self, password):
        salt, hash_ = self._password_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_

    @classmethod
    def register(cls, username, password):
        # In a real app, generate/store public/private keys here
        return cls(username, password, public_key="public_key_stub", private_key="private_key_stub")

    @staticmethod
    def login(user, password):
        return user.verify_password(password)

# Example user storage (in-memory for demo)
user_db = {}

def register_user(username, password):
    if username in user_db:
        print("Username already exists.")
        return None
    user = User.register(username, password)
    user_db[username] = user
    print("Registration successful.")
    return user

def login_gui():
    """GUI-based login function to authenticate the user with password masked as '*'."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis('off')
    plt.subplots_adjust(left=0.7, right=0.8, top=0.8, bottom=0.2)

    username_box = TextBox(plt.axes([0.3, 0.6, 0.4, 0.1]), 'Username:')
    password_box = TextBox(plt.axes([0.3, 0.4, 0.4, 0.1]), 'Password:')

    # Store the real password separately
    real_password = {'value': ''}

    # Overwrite the password box on every keystroke to show '*' only
    def on_password_submit(text):
        # This function is called when the user presses Enter in the password box
        pass  # Do nothing here

    def on_password_change(text):
        # Only update the real password if the change is a single character addition or deletion
        prev = real_password['value']
        if len(text) < len(prev):
            # Deletion
            real_password['value'] = prev[:len(text)]
        elif len(text) > len(prev):
            # Addition
            addition = text.replace('*', '')
            if addition:
                real_password['value'] += addition[-1]
        # Always mask the box
        password_box.set_val('*' * len(real_password['value']))

    password_box.on_submit(on_password_submit)
    password_box.on_text_change(on_password_change)

    login_status = {'authenticated': False}

    def submit(event):
        username = username_box.text
        password = real_password['value']
        user = user_db.get(username)
        if user and User.login(user, password):
            print("Login successful!")
            login_status['authenticated'] = True
            plt.close(fig)
        else:
            print("Invalid credentials. Try again.")
            username_box.set_val("")
            real_password['value'] = ""
            password_box.set_val("")

    submit_button = plt.axes([0.4, 0.2, 0.2, 0.1])
    button = plt.Button(submit_button, 'Login')
    button.on_clicked(submit)

    plt.show()
    return login_status['authenticated']

# Register a default user for demonstration
register_user("aaa", "aaa")