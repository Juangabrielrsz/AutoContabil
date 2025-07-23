import os
import shutil
import sys


def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_writable_db_path():

    user_dir = os.path.expanduser("~")
    app_data_dir = os.path.join(user_dir, "AutoContabil")
    os.makedirs(app_data_dir, exist_ok=True)
    db_path = os.path.join(app_data_dir, "database.db")

    if not os.path.exists(db_path):
        shutil.copy(resource_path("app/database.db"), db_path)

    return db_path
