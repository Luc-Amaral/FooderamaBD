from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from flask_login import current_user, login_required
from app.db_config import get_db_connection
import uuid
import calendar

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/cadastrar_pagamento', methods=['GET', 'POST'])
@login_required
def cadastrar_pagamento():
    if request.method == 'POST':
        # Verificar se o campo tipo_metodo está presente
        if 'tipo_metodo' not in request.form:
            flash('Selecione um tipo de método de pagamento.', 'error')
            return redirect('/cadastrar_pagamento')
            
        tipo_metodo = request.form['tipo_metodo']
        
        if not tipo_metodo:
            flash('Selecione um tipo de método de pagamento.', 'error')
            return redirect('/cadastrar_pagamento')
        
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            id_metodo_pagamento = str(uuid.uuid4())

            # Inserir método de pagamento
            cursor.execute("""
                INSERT INTO metodo_pagamento (ID_MetodoPagamento, ID_Cliente_FK, TipoMetodo)
                VALUES (%s, %s, %s)
            """, (id_metodo_pagamento, current_user.id, tipo_metodo))
            conn.commit()

            # Se for cartão (Débito ou Crédito), inserir dados do cartão
            if tipo_metodo in ['Debito', 'Credito']:
                numero_cartao = request.form['numero_cartao'].replace(' ', '')  # Remove espaços
                nome_portador = request.form['nome_portador']
                data_vencimento_raw = request.form['data_vencimento']
                cvv = request.form['cvv']
                
             
                if '/' in data_vencimento_raw and len(data_vencimento_raw) == 5:
                    mes, ano = data_vencimento_raw.split('/')
                    ano_completo = f"20{ano}" if int(ano) < 50 else f"19{ano}"
                    ultimo_dia = calendar.monthrange(int(ano_completo), int(mes))[1]
                    data_vencimento = f"{ano_completo}-{mes.zfill(2)}-{ultimo_dia:02d}"
                else:
                    data_vencimento = data_vencimento_raw

                id_cartao = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO cartao (ID_Cartao, ID_MetodoPagamento_FK, NumeroCartao, NomePortador, DataVencimento, CVV, TipoCartao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (id_cartao, id_metodo_pagamento, numero_cartao, nome_portador, data_vencimento, cvv, tipo_metodo))
                conn.commit()

            flash('Método de pagamento cadastrado com sucesso!', 'success')

        except Exception as e:
            conn.rollback()
            print(f"Erro ao cadastrar método de pagamento: {e}")  # Debug
            flash('Erro ao cadastrar método de pagamento. Verifique os dados informados.', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('payment.cadastrar_pagamento'))

    # Buscar métodos de pagamento do usuário
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mp.ID_MetodoPagamento, mp.TipoMetodo,
               c.NumeroCartao, c.NomePortador, c.DataVencimento
        FROM metodo_pagamento mp
        LEFT JOIN cartao c ON mp.ID_MetodoPagamento = c.ID_MetodoPagamento_FK
        WHERE mp.ID_Cliente_FK = %s
        ORDER BY mp.TipoMetodo
    """, (current_user.id,))
    metodos_pagamento = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('cadastrar_pagamento.html', metodos_pagamento=metodos_pagamento)

@payment_bp.route('/excluir_pagamento/<metodo_id>', methods=['POST'])
@login_required
def excluir_pagamento(metodo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Primeiro, verificar se o método pertence ao usuário atual
        cursor.execute("""
            SELECT ID_MetodoPagamento FROM metodo_pagamento 
            WHERE ID_MetodoPagamento = %s AND ID_Cliente_FK = %s
        """, (metodo_id, current_user.id))
        
        if not cursor.fetchone():
            flash('Método de pagamento não encontrado.', 'error')
            return redirect('/cadastrar_pagamento')
        
        # Excluir dados do cartão associado (se houver)
        cursor.execute("""
            DELETE FROM cartao WHERE ID_MetodoPagamento_FK = %s
        """, (metodo_id,))
        
        # Excluir o método de pagamento
        cursor.execute("""
            DELETE FROM metodo_pagamento WHERE ID_MetodoPagamento = %s
        """, (metodo_id,))
        
        conn.commit()
        flash('Método de pagamento excluído com sucesso!', 'success')
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao excluir método de pagamento: {e}")
        flash('Erro ao excluir método de pagamento.', 'error')
    finally:
        cursor.close()
        conn.close()
    
    return redirect('/cadastrar_pagamento')

@payment_bp.route('/api/metodos_pagamento')
@login_required
def api_metodos_pagamento():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT mp.ID_MetodoPagamento, mp.TipoMetodo,
               c.NumeroCartao, c.NomePortador
        FROM metodo_pagamento mp
        LEFT JOIN cartao c ON mp.ID_MetodoPagamento = c.ID_MetodoPagamento_FK
        WHERE mp.ID_Cliente_FK = %s
        ORDER BY mp.TipoMetodo
    """, (current_user.id,))
    metodos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(metodos)