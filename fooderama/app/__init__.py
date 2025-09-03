from flask import Flask
from flask_cors import CORS  # Importa o CORS
from app.routes import setup_routes
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.secret_key = 'sua_chave_secreta_aqui'
    CORS(app)  # Adiciona suporte a CORS para toda a aplicação
    setup_routes(app)
    return app


login_manager = LoginManager()

