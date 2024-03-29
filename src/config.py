import requests
import pandas as pd
import numpy as np
from io import BytesIO

from flask import *
from flask_bcrypt import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, EmailField

from wtforms.validators import InputRequired, Length, ValidationError, Email 

from os.path import abspath, join
from os import listdir
from base64 import b64encode
from joblib import load
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
from keras.applications.vgg16 import VGG16, preprocess_input
from PIL import Image
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


fertilizer_model_dir = "models/fertilizer.pkl"

d_model_potato_dir = "models/disease/potato.h5"
d_model_apple_dir = "models/disease/apple.h5"
d_model_rice_dir = "models/disease/rice.h5"
d_model_corn_dir = "models/disease/corn.h5"
d_model_tomato_dir = "models/disease/tomato.h5"

market_dir = 'models/market'