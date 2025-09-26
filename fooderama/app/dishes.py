from flask import Blueprint, render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
from app.models import Restaurante
import uuid

dishes_bp = Blueprint('dishes', __name__)

@dishes_bp.route('/cadastrar_comida')
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

@dishes_bp.route('/submit_food', methods=['POST'])
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

    return redirect(url_for('dishes.cadastrar_comida'))

@dishes_bp.route('/editar_prato/<string:food_id>', methods=['GET', 'POST'])
@login_required
def editar_prato(food_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Carregar os dados do prato específico
    cursor.execute("SELECT * FROM prato WHERE ID_Prato = %s AND ID_Restaurante_FK = %s", (food_id, current_user.id))
    food = cursor.fetchone()

    if food is None:
        flash('Prato não encontrado ou você não tem permissão para editar esse prato.', 'danger')
        return redirect(url_for('dishes.cadastrar_comida'))

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

        return redirect(url_for('dishes.cadastrar_comida'))

    # Se for GET, exibir o formulário com os dados do prato
    cursor.close()
    conn.close()
    return render_template('editar_prato.html', food=food, tipos_prato=tipos_prato)

@dishes_bp.route('/alterar_status/<prato_id>')
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

    return redirect(url_for('dishes.cadastrar_comida'))