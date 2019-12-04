# coding: UTF-8
from flask import (
    Flask, render_template,
    redirect, url_for, request,
    session, flash, make_response
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, logout_user
from werkzeug.security import *
import numpy as np
from datetime import *

from google_calendar import holiday

app = Flask(__name__)