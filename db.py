import mysql.connector
import logging
from configparser import ConfigParser


logging.basicConfig(level = logging.INFO)

def load_settings():
    """
    Loads settings from files

    :return: dictionary with settings key-value pairs.
    """

    config = ConfigParser()
    config.read("settings.ini")

    return {
        "host":config.get("mysql","host"),
        "database": config.get("mysql","database"),
        "user":config.get("mysql","user"),
        "password":config.get("mysql","password")
    }

def connect():
    """
    Connects user to Database.

    :return: Mysql connection.
    """
    conn = None
    settings = load_settings()
    params = {
        "host" : settings["host"],
        "db": settings["database"],
        "user": settings["user"],
        "passwd": settings["password"],
        "auth_plugin":"mysql_native_password"
    }
    try:
        conn = mysql.connector.connect(
            host=params["host"],
            user=params["user"],
            passwd=params["passwd"],
            db = params["db"],
            auth_plugin='mysql_native_password')
        logging.info("Connection Succesfullt set!")
        return conn
    except Exception as e:
        logging.error(e)

