from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
from app.models import Cliente

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    if not isinstance(current_user, Cliente):
        flash('Apenas clientes podem enviar feedback.', 'danger')
        return redirect(url_for('feedback.feedback', restaurant_id=request.args.get('restaurant_id')))

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
        return redirect(url_for('feedback.feedback', restaurant_id=restaurant_id))

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
        return redirect(url_for('feedback.feedback', restaurant_id=restaurant_id))

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

    return redirect(url_for('feedback.feedback', restaurant_id=restaurant_id))

@feedback_bp.route('/feedback')
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