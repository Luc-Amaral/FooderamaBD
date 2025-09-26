from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/listar_Lojas')
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

@main_bp.route('/pratos_por_tipo')
@login_required
def pratos_por_tipo():
    food_type = request.args.get('tipo', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if food_type:
        # Busca todos os pratos do tipo especificado, junto com o nome do restaurante
        cursor.execute("""
            SELECT p.*, r.NomeRestaurante, tp.Tipo
            FROM prato p
            JOIN restaurante r ON p.ID_Restaurante_FK = r.ID_Restaurante
            JOIN tipo_prato tp ON p.ID_TipoPrato_FK = tp.ID_TipoPrato
            WHERE tp.Tipo = %s AND p.StatusDisponibilidade = 1 AND p.Estoque > 0
            ORDER BY p.Nome
        """, (food_type,))
        pratos = cursor.fetchall()
    else:
        pratos = []
    
    cursor.close()
    conn.close()
    
    return render_template('pratos_por_tipo.html', pratos=pratos, tipo=food_type)

@main_bp.route('/restaurant')
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

@main_bp.route('/alterar_endereco/<endereco_id>', methods=['POST'])
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
    return redirect(url_for('main.cadastrar_endereco'))

@main_bp.route('/cadastrar_endereco', methods=['GET', 'POST'])
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

        return redirect(url_for('main.cadastrar_endereco'))

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

# APIs
@main_bp.route('/api/users', methods=['GET'])
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

@main_bp.route('/api/enderecos')
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

@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404