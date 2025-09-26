from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
from app.models import Cliente, Restaurante
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/finalizar_compra', methods=['POST'])
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
            INSERT INTO pedido (ID_Pedido, ID_Cliente_FK, ID_Endereco_FK, ID_MetodoPagamento_FK, Data, Hora, status)
            VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), 'PENDENTE')
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

@orders_bp.route('/aceitar_pedido/<pedido_id>', methods=['POST'])
@login_required
def aceitar_pedido(pedido_id):
    if not isinstance(current_user, Restaurante):
        flash('Apenas restaurantes podem aceitar pedidos.', 'danger')
        return redirect(url_for('main.index'))

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

    return redirect(url_for('orders.historico_rest'))

@orders_bp.route('/recusar_pedido/<pedido_id>', methods=['POST'])
@login_required
def recusar_pedido(pedido_id):
    if not isinstance(current_user, Restaurante):
        flash('Apenas restaurantes podem recusar pedidos.', 'danger')
        return redirect(url_for('main.index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            SET p.status = 'RECUSADO'
            WHERE p.ID_Pedido = %s AND pr.ID_Restaurante_FK = %s
        """, (pedido_id, current_user.id))

        if cursor.rowcount == 0:
            flash('Pedido não encontrado ou não pertence ao seu restaurante.', 'warning')
        else:
            conn.commit()
            flash('Pedido recusado com sucesso!', 'success')

    except Exception as e:
        conn.rollback()
        flash(f'Erro ao recusar pedido: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('orders.historico_rest'))

@orders_bp.route('/historico_rest')
@login_required
def historico_rest():
    if not isinstance(current_user, Restaurante):
        flash('Apenas restaurantes podem acessar o histórico de pedidos.', 'danger')
        return redirect(url_for('main.index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Query direta para pedidos pendentes com totais já calculados
        cursor.execute("""
            SELECT DISTINCT 
                p.ID_Pedido, 
                mp.TipoMetodo as payment_method, 
                p.Data as date, 
                p.Hora as time, 
                p.status as status,
                ROUND((
                    SELECT SUM(pr.Preco * i.Quantidade) * 0.97
                    FROM item i
                    JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                    WHERE i.ID_Pedido_FK = p.ID_Pedido
                ), 2) as total
            FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            JOIN metodo_pagamento mp ON p.ID_MetodoPagamento_FK = mp.ID_MetodoPagamento
            WHERE p.status = 'PENDENTE' AND pr.ID_Restaurante_FK = %s
        """, (current_user.id,))
        orders = cursor.fetchall()

        # Buscar histórico de pedidos para o restaurante atual com totais calculados diretamente
        cursor.execute("""
            SELECT DISTINCT 
                p.ID_Pedido, 
                mp.TipoMetodo as payment_method, 
                p.Data as date, 
                p.Hora as time, 
                p.status as status,
                ROUND((
                    SELECT SUM(pr.Preco * i.Quantidade) * 0.97
                    FROM item i
                    JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                    WHERE i.ID_Pedido_FK = p.ID_Pedido
                ), 2) as total
            FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            JOIN metodo_pagamento mp ON p.ID_MetodoPagamento_FK = mp.ID_MetodoPagamento
            WHERE p.status != 'PENDENTE' AND pr.ID_Restaurante_FK = %s
        """, (current_user.id,))
        historical_orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('historico_rest.html', orders=orders, historical_orders=historical_orders)
    
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"ERRO na rota historico_rest: {str(e)}")
        flash(f'Erro ao carregar histórico: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@orders_bp.route('/historico_cliente')
@login_required
def historico_cliente():
    if not isinstance(current_user, Cliente):
        flash('Apenas clientes podem acessar o histórico de pedidos.', 'danger')
        return redirect(url_for('main.index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Buscar histórico de pedidos aceitos do cliente com total calculado diretamente
        cursor.execute("""
            SELECT 
                p.ID_Pedido, 
                mp.TipoMetodo as payment_method, 
                p.Data as date, 
                p.Hora as time, 
                p.status,
                ROUND((
                    SELECT SUM(pr.Preco * i.Quantidade)
                    FROM item i
                    JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                    WHERE i.ID_Pedido_FK = p.ID_Pedido
                ), 2) as total
            FROM pedido p
            JOIN metodo_pagamento mp ON p.ID_MetodoPagamento_FK = mp.ID_MetodoPagamento
            WHERE p.ID_Cliente_FK = %s AND p.status = 'ACEITO'
        """, (current_user.id,))
        orders = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('historico_cliente.html', orders=orders)
    
    except Exception as e:
        cursor.close()
        conn.close()
        print(f"ERRO na rota historico_cliente: {str(e)}")
        flash(f'Erro ao carregar histórico: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

# APIs relacionadas a pedidos
@orders_bp.route('/api/get_restaurant_orders')
@login_required
def get_restaurant_orders():
    """API para obter pedidos do restaurante em JSON (para atualização dinâmica)"""
    if not isinstance(current_user, Restaurante):
        return jsonify({'error': 'Acesso negado - apenas restaurantes'}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query direta para evitar problemas com procedimentos
        cursor.execute("""
            SELECT DISTINCT 
                p.ID_Pedido, 
                mp.TipoMetodo as payment_method, 
                p.Data as date, 
                p.Hora as time, 
                p.status as status,
                ROUND((
                    SELECT SUM(pr.Preco * i.Quantidade) * 0.97
                    FROM item i
                    JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
                    WHERE i.ID_Pedido_FK = p.ID_Pedido
                ), 2) as total
            FROM pedido p
            JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
            JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
            JOIN metodo_pagamento mp ON p.ID_MetodoPagamento_FK = mp.ID_MetodoPagamento
            WHERE p.status = 'PENDENTE' AND pr.ID_Restaurante_FK = %s
        """, (current_user.id,))
        orders = cursor.fetchall()

        # Converter data e hora para string para JSON
        for order in orders:
            order['date'] = str(order['date'])
            order['time'] = str(order['time'])

        cursor.close()
        conn.close()

        return jsonify({'orders': orders})

    except Exception as e:
        print(f"DEBUG: Erro na API get_restaurant_orders: {str(e)}")
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/api/check_new_orders')
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

@orders_bp.route('/api/get_orders_status')
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