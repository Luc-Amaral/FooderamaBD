from flask_login import LoginManager
from app.db_config import get_db_connection
from app.models import Cliente, Restaurante

# Importar todos os blueprints
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.dishes import dishes_bp
from app.routes.orders import orders_bp
from app.routes.payment import payment_bp
from app.routes.feedback import feedback_bp

def setup_routes(app):
    # Configurar o Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.autenticar_login'  # Atualizado para usar o blueprint

    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Busca na tabela cliente
            cursor.execute("SELECT * FROM cliente WHERE ID_Cliente = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return Cliente(
                    id_cliente=row['ID_Cliente'],
                    cpf=row['CPF'],
                    email=row['Email'],
                    senha=row['Senha'],
                    telefone=row['Telefone'],
                    nome=row['Nome'],
                    sobrenome=row['Sobrenome']
                )
            
            # Se não encontrar na tabela cliente, busca na tabela restaurante
            cursor.execute("SELECT * FROM restaurante WHERE ID_Restaurante = %s", (user_id,))
            row = cursor.fetchone()
            if row:
                return Restaurante(
                    id_restaurante=row['ID_Restaurante'],
                    id_endereco=row['ID_Endereco_FK'],
                    nome_restaurante=row['NomeRestaurante'],
                    email=row['Email'],
                    senha=row['Senha'],  # Não gere hash novamente ao carregar do banco
                    telefone=row['Telefone']
                )
            
            return None
        finally:
            cursor.close()
            conn.close()

    # Registrar todos os blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dishes_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(feedback_bp)