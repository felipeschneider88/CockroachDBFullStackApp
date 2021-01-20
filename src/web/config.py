"""
Library for flask configuration.
"""
from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path('.env'), override=True)


class Config:
    """
    Flask configuration class.
    """
    SECRET_KEY = environ['SECRET_KEY']
    # API_KEY = environ['API_KEY']
    DB_URI = environ['DB_URI']
