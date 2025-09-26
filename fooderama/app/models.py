from werkzeug.security import check_password_hash
from flask_login import UserMixin
from app.db_config import get_db_connection

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

def get_cliente_by_email(email):
    """Função utilitária para buscar cliente por email"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Busca na tabela cliente
        cursor.execute("SELECT * FROM cliente WHERE Email = %s", (email,))
        row = cursor.fetchone()
        if row:
            return Cliente(
                id_cliente=row['ID_Cliente'],
                cpf=row['CPF'],
                email=row['Email'],
                senha=row['Senha'],  # Não gere hash novamente ao carregar do banco
                telefone=row['Telefone'],
                nome=row['Nome'],
                sobrenome=row['Sobrenome']
            )

        # Se não encontrar na tabela cliente, busca na tabela restaurante
        cursor.execute("SELECT * FROM restaurante WHERE Email = %s", (email,))
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

def load_user(user_id):
    """Função para carregar usuário pelo ID (usada pelo Flask-Login)"""
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