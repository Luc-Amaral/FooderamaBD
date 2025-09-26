from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app.db_config import get_db_connection
from app.models import get_cliente_by_email
from datetime import datetime
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/autenticar_login', methods=['GET', 'POST'])
def autenticar_login():
    # Verifica se o usuário já está logado
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"DEBUG: Tentativa de login com email: {email}")
        
        # Busca o cliente pelo e-mail
        cliente = get_cliente_by_email(email)
        
        if cliente:
            print(f"DEBUG: Cliente encontrado: {cliente.email}")
            print(f"DEBUG: Verificando senha...")
            # Verifica a senha e realiza o login
            if cliente.verificar_senha(password):
                print(f"DEBUG: Senha correta, fazendo login")
                login_user(cliente)
                return redirect(url_for('main.index'))
            else:
                print(f"DEBUG: Senha incorreta")
                flash('Login falhou. Verifique o e-mail e a senha.')
        else:
            print(f"DEBUG: Cliente não encontrado")
            flash('Login falhou. Verifique o e-mail e a senha.')

    return render_template('login.html')

@auth_bp.route('/registerClient', methods=['GET', 'POST'])
def register_cliente():
    # Verifica se o usuário já está autenticado
    if current_user.is_authenticated:
        return redirect('/index')

    if request.method == 'POST':
        # Tratamento para dados enviados via formulário
        cpf = request.form['cpf']
        email = request.form['email']
        senha = generate_password_hash(request.form['password'])
        telefone = request.form['phone']
        nome = request.form['first-name']
        sobrenome = request.form['last-name']

        print(f"DEBUG CADASTRO: Tentativa de cadastro com email: {email}, telefone: {telefone}")

        # Dados do endereço
        rua = request.form['street']
        bairro = request.form['neighborhood']
        numero = request.form['number']
        cep = request.form['cep']

        # Conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verifica se o email ou telefone já existe nas tabelas cliente ou restaurante
            cursor.execute("""
                SELECT 1 FROM cliente WHERE Email = %s OR Telefone = %s
                UNION
                SELECT 1 FROM restaurante WHERE Email = %s OR Telefone = %s
            """, (email, telefone, email, telefone))
            
            existing = cursor.fetchone()
            print(f"DEBUG CADASTRO: Verificação de duplicatas - resultado: {existing}")
            
            if existing:
                print(f"DEBUG CADASTRO: Email ou telefone já cadastrado")
                raise Exception('Email ou telefone já cadastrado.')

            # Gera UUIDs para cliente e endereço
            id_cliente = str(uuid.uuid4())
            id_endereco = str(uuid.uuid4())

            print(f"DEBUG CADASTRO: Inserindo cliente com ID: {id_cliente}")

            # Insere o cliente na tabela cliente
            cursor.execute("""
                INSERT INTO cliente (ID_Cliente, CPF, Email, Senha, Telefone, Nome, Sobrenome)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_cliente, cpf, email, senha, telefone, nome, sobrenome))
            conn.commit()

            print(f"DEBUG CADASTRO: Cliente inserido com sucesso")

            # Verifica se todos os dados do endereço foram preenchidos
            if rua and bairro and numero and cep:
                # Insere o endereço na tabela endereco
                cursor.execute("""
                    INSERT INTO endereco (ID_Endereco, Rua, Numero, Bairro, CEP)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_endereco, rua, numero, bairro, cep))
                conn.commit()

                # Cria o vínculo entre o cliente e o endereço
                cursor.execute("""
                    INSERT INTO endereco_cliente (ID_Endereco_FK, ID_Cliente_FK, Data_Atualizacao)
                    VALUES (%s, %s, NOW())
                """, (id_endereco, id_cliente))
                conn.commit()

                print(f"DEBUG CADASTRO: Endereço inserido com sucesso")
                flash('Registro realizado com sucesso!')
            else:
                flash('Todos os campos de endereço são obrigatórios.')
                return render_template('registerCli.html')

            # Verificação final: confirma se o cliente foi inserido
            cursor.execute("SELECT COUNT(*) FROM cliente WHERE Email = %s", (email,))
            count = cursor.fetchone()[0]
            print(f"DEBUG CADASTRO: Verificação final - cliente encontrado no banco: {count > 0}")

        except Exception as e:
            conn.rollback()
            # Mensagem de erro para depuração
            error_message = f'Erro ao registrar cliente: {str(e)}'
            print(f"DEBUG CADASTRO: {error_message}")
            flash(error_message)
            return jsonify({'error': error_message}), 400
        finally:
            cursor.close()
            conn.close()
            return redirect(url_for('auth.autenticar_login'))

    # Retorna a página de registro
    return render_template('registerCli.html')

@auth_bp.route('/registerRest', methods=['GET', 'POST'])
def register_restaurante():
    if current_user.is_authenticated:
        return redirect('/index')

    if request.method == 'POST':
        # Tratamento para dados enviados via formulário
        nome_restaurante = request.form['name-restaurant']
        email = request.form['email']
        senha = generate_password_hash(request.form['password'])
        telefone = request.form['phone']

        # Dados do endereço
        rua = request.form['street']
        bairro = request.form['neighborhood']
        numero = request.form['number']
        cep = request.form['cep']

        # Dados dos horários de funcionamento
        dias_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        dias_semana_db = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        horarios = []
        for i, dia in enumerate(dias_semana):
            ativo = request.form.get(f'{dia}_ativo') == 'on'
            if ativo:
                abertura = request.form.get(f'{dia}_abertura')
                fechamento = request.form.get(f'{dia}_fechamento')
                if abertura and fechamento:
                    horarios.append({
                        'dia': dias_semana_db[i],
                        'abertura': format_time(abertura),
                        'fechamento': format_time(fechamento),
                        'status': 1
                    })

        # Conexão com o banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verifica se o email ou telefone já existe nas tabelas cliente ou restaurante
            cursor.execute("""
                SELECT 1 FROM cliente WHERE Email = %s OR Telefone = %s
                UNION
                SELECT 1 FROM restaurante WHERE Email = %s OR Telefone = %s
            """, (email, telefone, email, telefone))
            if cursor.fetchone():
                raise Exception('Email ou telefone já cadastrado.')

            # Gera UUIDs para restaurante e endereço
            id_restaurante = str(uuid.uuid4())
            id_endereco = str(uuid.uuid4())

            # Insere o endereço na tabela endereco
            cursor.execute("""
                INSERT INTO endereco (ID_Endereco, Rua, Numero, Bairro, CEP)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_endereco, rua, numero, bairro, cep))

            # Insere os dados do restaurante na tabela restaurante (sem tipo culinária e horários)
            cursor.execute("""
                INSERT INTO restaurante (ID_Restaurante, ID_Endereco_FK, NomeRestaurante, Email, Senha, Telefone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_restaurante, id_endereco, nome_restaurante, email, senha, telefone))

            # Insere os horários de funcionamento na tabela horafuncionamento
            for horario in horarios:
                id_hora_funcionamento = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO horafuncionamento (ID_HoraFuncionamento, ID_Restaurante_FK, DiaSemana, HoraAbertura, HoraFechamento, Status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_hora_funcionamento, id_restaurante, horario['dia'], horario['abertura'], horario['fechamento'], horario['status']))

            conn.commit()
            flash('Restaurante registrado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            error_message = f'Erro ao registrar restaurante: {str(e)}'
            flash(error_message, 'danger')
            return jsonify({'error': error_message}), 400
        finally:
            cursor.close()
            conn.close()
            return redirect(url_for('auth.autenticar_login'))

    return render_template('registerRest.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('main.index'))

def format_time(time_str):
    # Garantir que a string do tempo tenha o formato XX:XX
    try:
        # Tentar parse a string no formato HH:MM
        time_obj = datetime.strptime(time_str, '%H:%M')
        return time_obj.strftime('%H:%M')  # Retorna o formato XX:XX
    except ValueError:
        return "00:00"  # Valor padrão caso haja erro no formato