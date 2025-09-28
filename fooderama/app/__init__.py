from flask import Flask
from flask_cors import CORS  # Importa o CORS
from app.routes import setup_routes
from flask_login import LoginManager
import datetime

def create_app():
    app = Flask(__name__)
    app.secret_key = 'sua_chave_secreta_aqui'
    CORS(app)  # Adiciona suporte a CORS para toda a aplicação
    
    # Filtro customizado para formatar horários
    @app.template_filter('format_time')
    def format_time(time_obj):
        if isinstance(time_obj, datetime.timedelta):
            # Converte timedelta para horas e minutos
            total_seconds = int(time_obj.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        return str(time_obj)
    
    setup_routes(app)
    return app


login_manager = LoginManager()

