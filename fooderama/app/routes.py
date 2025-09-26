from flask_login import LoginManager
from app.models import load_user
from app.auth import auth_bp
from app.main import main_bp
from app.dishes import dishes_bp
from app.orders import orders_bp
from app.payment import payment_bp
from app.feedback import feedback_bp

def setup_routes(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.autenticar_login'

    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)

    # Registrar os blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dishes_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(feedback_bp)