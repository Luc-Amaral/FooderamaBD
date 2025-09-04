from flask import render_template, flash, redirect, request, jsonify, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager,UserMixin
from app.db_config import get_db_connection  # Importa a conexão
from datetime import datetime
import uuid

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

def setup_routes(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'autenticar_login' 

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


    @app.route('/api/users', methods=['GET'])
    def get_all_users_api():
        # Conectando ao banco de dados
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Executando a consulta para selecionar todos os usuários
        cursor.execute("SELECT * FROM cliente")
        users = cursor.fetchall()
        
        # Fechando a conexão com o banco de dados
        cursor.close()
        conn.close()
        
        # Retornando os dados em formato JSON
        return jsonify(users)
    
    
    def get_cliente_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Use `dictionary=True` para retornar um dicionário

        try:
            # Busca na tabela cliente
            cursor.execute("SELECT * FROM cliente WHERE Email = %s", (email,))
            row = cursor.fetchone()
            if row:
                # Cria um objeto Cliente usando os valores recuperados do banco, sem gerar um novo hash para `senha`
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
                # Cria um objeto Restaurante usando os valores recuperados do banco, sem gerar um novo hash para `senha`
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
    
    @app.route('/autenticar_login', methods=['GET', 'POST'])
    def autenticar_login():
        # Verifica se o usuário já está logado
        if current_user.is_authenticated:
            return redirect('/')
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
                    return redirect('/')
                else:
                    print(f"DEBUG: Senha incorreta")
                    flash('Login falhou. Verifique o e-mail e a senha.')
            else:
                print(f"DEBUG: Cliente não encontrado")
                flash('Login falhou. Verifique o e-mail e a senha.')

        return render_template('login.html')
    
    
    @app.route('/registerClient', methods=['GET', 'POST'])
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
                return redirect(url_for('autenticar_login'))

        # Retorna a página de registro
        return render_template('registerCli.html')

    
    @app.route('/registerRest', methods=['GET', 'POST'])
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
                return redirect(url_for('autenticar_login'))

        return render_template('registerRest.html')


    def format_time(time_str):
        # Garantir que a string do tempo tenha o formato XX:XX
        try:
            # Tentar parse a string no formato HH:MM
            time_obj = datetime.strptime(time_str, '%H:%M')
            return time_obj.strftime('%H:%M')  # Retorna o formato XX:XX
        except ValueError:
            return "00:00"  # Valor padrão caso haja erro no fo
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Você foi desconectado.', 'success')
        return redirect('/')

    #rotas de template
    @app.route('/', )
    @app.route('/index', )
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/listar_Lojas')
    @login_required
    def listar_lojas():
        food_type = request.args.get('food-type', '').lower()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Busca restaurantes que tenham pratos do tipo selecionado
        if food_type:
            cursor.execute("""
                SELECT DISTINCT r.*, tp.Tipo as TipoComida
                FROM restaurante r
                JOIN prato p ON r.ID_Restaurante = p.ID_Restaurante_FK
                JOIN tipo_prato tp ON p.ID_TipoPrato_FK = tp.ID_TipoPrato
                WHERE LOWER(tp.Tipo) = %s
            """, (food_type,))
        else:
            # Se não há filtro, busca todos os restaurantes
            cursor.execute("SELECT *, NULL as TipoComida FROM restaurante")
        
        restaurantes = cursor.fetchall()
        
        # Dicionário para armazenar as médias das avaliações
        medias_avaliacoes = {}
        
        # Calcula a média das avaliações para cada restaurante
        for restaurante in restaurantes:
            cursor.execute("""
                SELECT AVG(Avaliacao) as media_avaliacao
                FROM feedback
                WHERE ID_Restaurante_FK = %s
            """, (restaurante['ID_Restaurante'],))
            media = cursor.fetchone()
            medias_avaliacoes[restaurante['ID_Restaurante']] = media['media_avaliacao'] if media['media_avaliacao'] is not None else 0
        
        cursor.close()
        conn.close()
        
        return render_template('listar_lojas.html', restaurantes=restaurantes, medias_avaliacoes=medias_avaliacoes, food_type=food_type)

    @app.route('/restaurant')
    @login_required
    def restaurant():
        restaurant_id = request.args.get('restaurant_id', '').lower()
        food_type = request.args.get('food-type', '').lower()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM prato WHERE ID_Restaurante_FK = %s", (restaurant_id,))
        pratos = cursor.fetchall()

        cursor.execute("SELECT * FROM restaurante WHERE ID_Restaurante = %s", (restaurant_id,))
        restaurante = cursor.fetchone()

        cursor.execute("""
            SELECT e.*
            FROM endereco e
            JOIN endereco_cliente ec ON e.ID_Endereco = ec.ID_Endereco_FK
            WHERE ec.ID_Cliente_FK = %s
            ORDER BY ec.Data_Atualizacao DESC
        """, (current_user.id,))

        enderecos = cursor.fetchall()
        print(f"DEBUG: Enderecos encontrados para cliente {current_user.id}: {enderecos}")

        cursor.close()
        conn.close()

        return render_template('restaurant.html', pratos=pratos, restaurante=restaurante, food_type=food_type, enderecos=enderecos)

    @app.route('/api/enderecos')
    @login_required
    def get_enderecos_api():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT e.*
                FROM endereco e
                JOIN endereco_cliente ec ON e.ID_Endereco = ec.ID_Endereco_FK
                WHERE ec.ID_Cliente_FK = %s
                ORDER BY ec.Data_Atualizacao DESC
            """, (current_user.id,))
            enderecos = cursor.fetchall()
            return jsonify(enderecos)
        finally:
            cursor.close()
            conn.close()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    

    @app.route('/cadastrar_comida')
    @login_required
    def cadastrar_comida():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Use `dictionary=True` para retornar um dicionário

        cursor.execute("SELECT * FROM prato WHERE ID_Restaurante_FK = %s", (current_user.id,))
        prato = cursor.fetchall()

        cursor.execute("SELECT * FROM restaurante WHERE ID_Restaurante = %s", (current_user.id,))
        restaurante = cursor.fetchone()

        # Buscar todos os tipos de prato disponíveis
        cursor.execute("SELECT * FROM tipo_prato ORDER BY Tipo")
        tipos_prato = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('cadastrar_comida.html', prato=prato, restaurante=restaurante, tipos_prato=tipos_prato)
    
    @app.route('/submit_food', methods=['POST'])
    @login_required
    def submit_food():
        # Extract form data
        food_name = request.form['food_name']
        food_type = request.form['food_type']  # ID do tipo de prato
        description = request.form['description']
        price = request.form['price']
        estoque = request.form['estoque']
        status = request.form['status']

        # Convert status to appropriate value
        status_value = 1 if status == 'ativo' else 0

        # Generate a new UUID for the food item
        food_id = str(uuid.uuid4())

        # Insert the new food item into the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO prato (ID_Prato, ID_Restaurante_FK, ID_TipoPrato_FK, Nome, Descricao, Preco, Estoque, StatusDisponibilidade)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (food_id, current_user.id, food_type, food_name, description, price, estoque, status_value))
            conn.commit()
            flash('Comida cadastrada com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao cadastrar comida: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('cadastrar_comida'))
    

    @app.route('/editar_prato/<string:food_id>', methods=['GET', 'POST'])
    @login_required
    def editar_prato(food_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Carregar os dados do prato específico
        cursor.execute("SELECT * FROM prato WHERE ID_Prato = %s AND ID_Restaurante_FK = %s", (food_id, current_user.id))
        food = cursor.fetchone()

        if food is None:
            flash('Prato não encontrado ou você não tem permissão para editar esse prato.', 'danger')
            return redirect(url_for('cadastrar_comida'))

        # Buscar todos os tipos de prato disponíveis para o formulário
        cursor.execute("SELECT * FROM tipo_prato ORDER BY Tipo")
        tipos_prato = cursor.fetchall()

        if request.method == 'POST':
            # Obter os novos dados do formulário
            food_name = request.form['food_name']
            food_type = request.form['food_type']  # ID do tipo de prato
            description = request.form['description']
            price = request.form['price']
            estoque = request.form['estoque']
            status = request.form['status']

            status_value = 1 if status == 'ativo' else 0

            # Atualizar os dados no banco de dados
            try:
                cursor.execute("""
                    UPDATE prato
                    SET Nome = %s, ID_TipoPrato_FK = %s, Descricao = %s, Preco = %s, Estoque = %s, StatusDisponibilidade = %s
                    WHERE ID_Prato = %s
                """, (food_name, food_type, description, price, estoque, status_value, food_id))
                conn.commit()
                flash('Comida atualizada com sucesso!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f'Erro ao atualizar comida: {str(e)}', 'danger')
            finally:
                cursor.close()
                conn.close()

            return redirect(url_for('cadastrar_comida'))

        # Se for GET, exibir o formulário com os dados do prato
        cursor.close()
        conn.close()
        return render_template('editar_prato.html', food=food, tipos_prato=tipos_prato)

    @app.route('/alterar_status/<prato_id>')
    @login_required
    def alterar_status(prato_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Chamar a função para alternar a disponibilidade
        cursor.execute("SELECT toggle_disponibilidade_prato(%s)", (prato_id,))
        cursor.fetchone()
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('cadastrar_comida'))
    
    @app.route('/finalizar_compra', methods=['POST'])
    @login_required
    def finalizar_compra():
        data = request.json
        payment_method = data.get('payment_method')
        cart_items = data.get('cart_items')

        if not cart_items:
            return jsonify({'error': 'Carrinho vazio'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Obter o ID do endereço mais recente do cliente
            cursor.execute("""
                SELECT ID_Endereco_FK FROM endereco_cliente
                WHERE ID_Cliente_FK = %s
                ORDER BY Data_Atualizacao DESC
                LIMIT 1
            """, (current_user.id,))
            endereco = cursor.fetchone()
            if not endereco:
                return jsonify({'error': 'Endereço não encontrado'}), 400
            id_endereco = endereco[0]

            # Gera UUID para o pedido
            id_pedido = str(uuid.uuid4())

            # Insere o pedido na tabela pedido com status = FINALIZADO
            cursor.execute("""
                INSERT INTO pedido (ID_Pedido, ID_Cliente_FK, ID_Endereco_FK, Data, Hora, FormaPagamento, status)
                VALUES (%s, %s, %s, CURDATE(), CURTIME(), %s, 'PENDENTE')
            """, (id_pedido, current_user.id, id_endereco, payment_method))
            conn.commit()

            # Insere os itens na tabela item
            for item in cart_items:
                cursor.execute("""
                    INSERT INTO item (ID_Item, ID_Pedido_FK, ID_Prato_FK, Quantidade)
                    VALUES (%s, %s, %s, %s)
                """, (str(uuid.uuid4()), id_pedido, item['id'], item['quantidade']))
            conn.commit()

            return jsonify({'message': 'Pedido enviado para aprovação'}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    
    @app.route('/alterar_endereco/<endereco_id>', methods=['POST'])
    @login_required
    def alterar_endereco(endereco_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Atualiza o endereço selecionado como o mais recente
            cursor.execute("""
                UPDATE endereco_cliente
                SET Data_Atualizacao = NOW()
                WHERE ID_Endereco_FK = %s AND ID_Cliente_FK = %s
            """, (endereco_id, current_user.id))
            conn.commit()
            flash('Endereço atualizado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao atualizar endereço: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

        # Obter a URL de origem (página anterior) para redirecionar o usuário
        origin = request.args.get('origin')
        if origin:
            return redirect(origin)  # Redireciona para a página anterior

        # Caso não tenha origem, redireciona para a página padrão
        return redirect(url_for('cadastrar_endereco'))
        

    @app.route('/cadastrar_endereco', methods=['GET', 'POST'])
    @login_required
    def cadastrar_endereco():
        if request.method == 'POST':
            rua = request.form['street']
            bairro = request.form['neighborhood']
            numero = request.form['number']
            cep = request.form['cep']

            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                id_endereco = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO endereco (ID_Endereco, Rua, Numero, Bairro, CEP)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_endereco, rua, numero, bairro, cep))
                conn.commit()

                cursor.execute("""
                    INSERT INTO endereco_cliente (ID_Endereco_FK, ID_Cliente_FK, Data_Atualizacao)
                    VALUES (%s, %s, NOW())
                """, (id_endereco, current_user.id))
                conn.commit()

            except Exception as e:
                conn.rollback()
            finally:
                cursor.close()
                conn.close()

            return redirect(url_for('cadastrar_endereco'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.ID_Endereco as id, e.Rua as rua, e.Numero as numero, e.Bairro as bairro, e.CEP as cep
            FROM endereco e
            JOIN endereco_cliente ec ON e.ID_Endereco = ec.ID_Endereco_FK
            WHERE ec.ID_Cliente_FK = %s
            ORDER BY ec.Data_Atualizacao DESC
        """, (current_user.id,))
        addresses = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template('cadastrar_endereco.html', addresses=addresses)
    

    @app.route('/aceitar_pedido/<pedido_id>', methods=['POST'])
    @login_required
    def aceitar_pedido(pedido_id):
        if not isinstance(current_user, Restaurante):
            flash('Apenas restaurantes podem aceitar pedidos.', 'danger')
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Atualizar o status do pedido para 'ACEITO'
            cursor.execute("""
                UPDATE pedido p
                JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
                JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                SET p.status = 'ACEITO'
                WHERE p.ID_Pedido = %s AND pr.ID_Restaurante_FK = %s
            """, (pedido_id, current_user.id))
            conn.commit()
            flash('Pedido aceito com sucesso.', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao aceitar o pedido: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('historico_rest'))

    @app.route('/recusar_pedido/<pedido_id>', methods=['POST'])
    @login_required
    def recusar_pedido(pedido_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE pedido
                SET status = 'RECUSADO'
                WHERE ID_Pedido = %s
            """, (pedido_id,))
            conn.commit()
            flash('Pedido recusado com sucesso!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Erro ao recusar pedido: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('historico_rest'))

  
    

    @app.route('/historico_rest')
    @login_required
    def historico_rest():
        if not isinstance(current_user, Restaurante):
            flash('Apenas restaurantes podem acessar o histórico de pedidos.', 'danger')
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar pedidos pendentes para o restaurante atual
        cursor.execute("""
            SELECT DISTINCT p.ID_Pedido, p.FormaPagamento as payment_method, p.Data as date, p.Hora as time, p.status as status
            FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            WHERE p.status = 'PENDENTE' AND pr.ID_Restaurante_FK = %s
        """, (current_user.id,))
        orders = cursor.fetchall()

        # Calcular o valor total de cada pedido pendente e subtrair 3%
        for order in orders:
            cursor.execute("CALL calcular_total_pedido(%s, @total)", (order['ID_Pedido'],))
            cursor.execute("SELECT @total AS total")
            total_result = cursor.fetchone()
            order['total'] = total_result['total'] * 0.97  # Subtrair 3%

        # Buscar histórico de pedidos para o restaurante atual
        cursor.execute("""
            SELECT DISTINCT p.ID_Pedido, p.FormaPagamento as payment_method, p.Data as date, p.Hora as time, p.status as status
            FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            WHERE p.status != 'PENDENTE' AND pr.ID_Restaurante_FK = %s
        """, (current_user.id,))
        historical_orders = cursor.fetchall()

        # Calcular o valor total de cada pedido histórico e subtrair 3%
        for order in historical_orders:
            cursor.execute("CALL calcular_total_pedido(%s, @total)", (order['ID_Pedido'],))
            cursor.execute("SELECT @total AS total")
            total_result = cursor.fetchone()
            order['total'] = total_result['total'] * 0.97  # Subtrair 3%

        cursor.close()
        conn.close()

        return render_template('historico_rest.html', orders=orders, historical_orders=historical_orders)
    

    @app.route('/submit_review', methods=['POST'])
    @login_required
    def submit_review():
        if not isinstance(current_user, Cliente):
            flash('Apenas clientes podem enviar feedback.', 'danger')
            return redirect(url_for('feedback', restaurant_id=request.args.get('restaurant_id')))

        rating = request.form['rating']
        review = request.form['review']
        date_str = request.form['date']
        time_str = request.form['time']
        restaurant_id = request.args.get('restaurant_id')

        # Verifica se o cliente já fez pelo menos um pedido completo no restaurante
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as count FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            WHERE p.ID_Cliente_FK = %s AND pr.ID_Restaurante_FK = %s
        """, (current_user.id, restaurant_id))
        result = cursor.fetchone()
        if result['count'] == 0:
            flash('Você precisa ter feito pelo menos um pedido completo neste restaurante para enviar um feedback.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('feedback', restaurant_id=restaurant_id))

        # Verifica se o cliente já deixou um feedback para o restaurante
        cursor.execute("""
            SELECT COUNT(*) as count FROM feedback
            WHERE ID_Cliente_FK = %s AND ID_Restaurante_FK = %s
        """, (current_user.id, restaurant_id))
        result = cursor.fetchone()
        if result['count'] > 0:
            flash('Você já deixou um feedback para este restaurante.', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('feedback', restaurant_id=restaurant_id))

        # Insere o feedback no banco de dados
        try:
            cursor.execute("""
                INSERT INTO feedback (ID_Cliente_FK, ID_Restaurante_FK, Avaliacao, Feedback, Data, Hora)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (current_user.id, restaurant_id, rating, review, date_str, time_str))
            conn.commit()
            flash('Feedback enviado com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao enviar feedback: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('feedback', restaurant_id=restaurant_id))


    @app.route('/feedback')
    @login_required
    def feedback():
        restaurant_id = request.args.get('restaurant_id')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Busca os feedbacks do restaurante
        cursor.execute("""
            SELECT f.Avaliacao as nota, f.Feedback as comentario, f.Data as data, f.Hora as hora, c.Nome as usuario_nome, LEFT(c.Nome, 1) as usuario_inicial
            FROM feedback f
            JOIN cliente c ON f.ID_Cliente_FK = c.ID_Cliente
            WHERE f.ID_Restaurante_FK = %s
        """, (restaurant_id,))
        feedbacks = cursor.fetchall()
        
        # Busca informações do restaurante
        cursor.execute("SELECT * FROM restaurante WHERE ID_Restaurante = %s", (restaurant_id,))
        restaurante = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return render_template('feedback.html', feedbacks=feedbacks, restaurante=restaurante)



    @app.route('/historico_cliente')
    @login_required
    def historico_cliente():
        if not isinstance(current_user, Cliente):
            flash('Apenas clientes podem acessar o histórico de pedidos.', 'danger')
            return redirect(url_for('index'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar histórico de pedidos aceitos do cliente
        cursor.execute("""
            SELECT ID_Pedido, FormaPagamento as payment_method, Data as date, Hora as time, status
            FROM pedido
            WHERE ID_Cliente_FK = %s AND status = 'ACEITO'
        """, (current_user.id,))
        orders = cursor.fetchall()

        # Calcular o valor total de cada pedido
        for order in orders:
            cursor.execute("CALL calcular_total_pedido(%s, @total)", (order['ID_Pedido'],))
            cursor.execute("SELECT @total AS total")
            total_result = cursor.fetchone()
            order['total'] = total_result['total']

        cursor.close()
        conn.close()

        return render_template('historico_cliente.html', orders=orders)

    @app.route('/api/check_new_orders')
    @login_required
    def check_new_orders():
        """Endpoint para verificar novos pedidos (para restaurantes)"""
        print(f"DEBUG: current_user type: {type(current_user)}")
        print(f"DEBUG: current_user: {current_user}")
        print(f"DEBUG: isinstance Restaurante: {isinstance(current_user, Restaurante)}")
        
        if not isinstance(current_user, Restaurante):
            return jsonify({'error': 'Acesso negado - apenas restaurantes'}), 403
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            print(f"DEBUG: Restaurante ID: {current_user.id}")
            
            # Buscar pedidos pendentes para este restaurante
            cursor.execute("""
                SELECT COUNT(*) as novos_pedidos
                FROM pedido p
                JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
                JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                WHERE pr.ID_Restaurante_FK = %s AND p.status = 'PENDENTE'
            """, (current_user.id,))
            
            result = cursor.fetchone()
            novos_pedidos = result['novos_pedidos'] if result else 0
            
            print(f"DEBUG: Novos pedidos encontrados: {novos_pedidos}")
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'novos_pedidos': novos_pedidos,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"DEBUG: Erro na API check_new_orders: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/get_orders_status')
    @login_required 
    def get_orders_status():
        """Endpoint para obter status atualizado de todos os pedidos"""
        if not isinstance(current_user, Restaurante):
            return jsonify({'error': 'Acesso negado - apenas restaurantes'}), 403
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Buscar todos os pedidos para este restaurante
            cursor.execute("""
                SELECT p.ID_Pedido, p.status, p.Data, p.Hora, 
                       c.Nome as cliente_nome, pr.Nome as prato_nome,
                       p.Quantidade, pr.Preco
                FROM pedido p
                JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
                JOIN prato pr ON p.ID_Prato_FK = pr.ID_Prato
                WHERE pr.ID_Restaurante_FK = %s
                ORDER BY p.Data DESC, p.Hora DESC
                LIMIT 10
            """, (current_user.id,))
            
            pedidos = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'pedidos': pedidos,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500










