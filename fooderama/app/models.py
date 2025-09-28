from flask_login import UserMixin
from werkzeug.security import check_password_hash

class Cliente(UserMixin):
    def __init__(self, id_cliente, cpf, email, senha, telefone, nome, sobrenome):
        self.id = id_cliente
        self.cpf = cpf
        self.email = email
        self.senha_hash = senha  # Armazena a senha como hash
        self.telefone = telefone
        self.nome = nome
        self.sobrenome = sobrenome

    def verificar_senha(self, senha):
        """Verifica a senha fornecida em relação ao hash armazenado"""
        print(f"DEBUG: Verificando senha. Hash armazenado: {self.senha_hash}")
        print(f"DEBUG: Senha fornecida: {senha}")
        resultado = check_password_hash(self.senha_hash, senha)
        print(f"DEBUG: Resultado da verificação: {resultado}")
        return resultado

    def get_id(self):
        """Método necessário para `UserMixin`"""
        return str(self.id)
    
    @property
    def is_client(self):
        return True
    
class Restaurante(UserMixin):
    def __init__(self, id_restaurante, id_endereco, nome_restaurante, email, senha, telefone):
        self.id = id_restaurante
        self.id_endereco = id_endereco
        self.nome_restaurante = nome_restaurante
        self.email = email
        self.senha_hash = senha
        self.telefone = telefone

    def verificar_senha(self, senha):
        """Verifica a senha fornecida em relação ao hash armazenado"""
        return check_password_hash(self.senha_hash, senha)

    def get_id(self):
        """Método necessário para `UserMixin`"""
        return str(self.id)
    
    @property
    def is_client(self):
        return False