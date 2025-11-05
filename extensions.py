#se crea el objeto db para la base de datos y evitar ciclos de importacion
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()