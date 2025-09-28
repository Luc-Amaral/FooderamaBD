from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
import uuid

dishes_bp = Blueprint('dishes', __name__)

@dishes_bp.route('/cadastrar_comida')
@login_required
def cadastrar_comida():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Use `dictionary=True` para retornar um dicionário

    cursor.execute("""
        SELECT p.*, tp.Tipo as TipoPrato 
        FROM prato p 
        JOIN tipo_prato tp ON p.ID_TipoPrato_FK = tp.ID_TipoPrato 
        WHERE p.ID_Restaurante_FK = %s
    """, (current_user.id,))
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
    # O trigger automaticamente ajustará StatusDisponibilidade baseado no estoque
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

        # Convert status to appropriate value
        # O trigger automaticamente ajustará StatusDisponibilidade baseado no estoque
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

@dishes_bp.route('/editarHorario')
@login_required
def editarHorario():
    """Página para editar horários de funcionamento do restaurante"""
    # Verificar se é um restaurante
    if current_user.is_client:
        flash('Acesso negado. Apenas restaurantes podem editar horários.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('editarHorario.html')

@dishes_bp.route('/api/horarios/<restaurante_id>')
def get_horarios(restaurante_id):
    """Busca os horários de funcionamento de um restaurante"""
    try:
        print(f"DEBUG: Buscando horários para restaurante {restaurante_id}")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT DiaSemana, HoraAbertura, HoraFechamento, Status
            FROM horafuncionamento 
            WHERE ID_Restaurante_FK = %s
            ORDER BY FIELD(DiaSemana, 'Segunda', 'Terca', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo')
        """, (restaurante_id,))
        
        horarios = cursor.fetchall()
        print(f"DEBUG: Horários encontrados: {horarios}")
        
        # Converter time objects para string
        for horario in horarios:
            if horario['HoraAbertura']:
                horario['HoraAbertura'] = str(horario['HoraAbertura'])
            if horario['HoraFechamento']:
                horario['HoraFechamento'] = str(horario['HoraFechamento'])
        
        print(f"DEBUG: Retornando horários: {horarios}")
        return jsonify(horarios)
        
    except Exception as e:
        print(f"Erro ao buscar horários: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@dishes_bp.route('/api/salvar_horarios', methods=['POST'])
def salvar_horarios():
    """Salva os horários de funcionamento de um restaurante"""
    try:
        print("DEBUG: Recebendo dados para salvar horários")
        data = request.get_json()
        print(f"DEBUG: Dados recebidos: {data}")
        
        restaurante_id = data.get('restaurante_id')
        horarios = data.get('horarios')
        
        print(f"DEBUG: Restaurante ID: {restaurante_id}")
        print(f"DEBUG: Horários: {horarios}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Primeiro, deletar todos os horários existentes do restaurante
        print("DEBUG: Deletando horários existentes")
        cursor.execute("DELETE FROM horafuncionamento WHERE ID_Restaurante_FK = %s", (restaurante_id,))
        
        # Inserir os novos horários
        print("DEBUG: Inserindo novos horários")
        for horario in horarios:
            id_hora_funcionamento = str(uuid.uuid4())
            print(f"DEBUG: Inserindo horário: {horario}")
            cursor.execute("""
                INSERT INTO horafuncionamento (ID_HoraFuncionamento, ID_Restaurante_FK, DiaSemana, HoraAbertura, HoraFechamento, Status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_hora_funcionamento, restaurante_id, horario['dia'], horario['abertura'], horario['fechamento'], horario['status']))
        
        conn.commit()
        print("DEBUG: Horários salvos com sucesso")
        return jsonify({'success': True, 'message': 'Horários salvos com sucesso!'})
        
    except Exception as e:
        print(f"Erro ao salvar horários: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()