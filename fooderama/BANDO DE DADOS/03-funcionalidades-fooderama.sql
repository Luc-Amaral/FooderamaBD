-- ===============================================================
-- FUNCIONALIDADES AVANÇADAS DO SISTEMA FOODERAMA
-- Arquivo: funcionalidades_fooderama.sql
-- Criado em: 01/09/2025
-- Descrição: Triggers, funções e procedimentos para o sistema
-- ===============================================================



-- ===============================================================
-- TRIGGERS DE VALIDAÇÃO
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- TRIGGER: Verificação de estoque antes de inserir item no pedido
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_verificar_estoque_item //

CREATE TRIGGER tr_verificar_estoque_item
BEFORE INSERT ON item
FOR EACH ROW
BEGIN
    DECLARE estoque_disponivel INT DEFAULT 0;
    DECLARE nome_prato VARCHAR(100);
    
    -- Buscar o estoque disponível do prato
    SELECT Estoque, Nome
    INTO estoque_disponivel, nome_prato
    FROM prato 
    WHERE ID_Prato = NEW.ID_Prato_FK;
    
    -- Verificar se há estoque suficiente
    IF estoque_disponivel <= 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = CONCAT('Estoque insuficiente para o prato: ', nome_prato, '. Estoque atual: ', estoque_disponivel);
    END IF;
    
    -- Verificar se a quantidade solicitada não excede o estoque
    IF NEW.Quantidade > estoque_disponivel THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = CONCAT('Quantidade solicitada (', NEW.Quantidade, ') excede o estoque disponível (', estoque_disponivel, ') para o prato: ', nome_prato);
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Verificação de estoque antes de atualizar item no pedido
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_verificar_estoque_item_update //

CREATE TRIGGER tr_verificar_estoque_item_update
BEFORE UPDATE ON item
FOR EACH ROW
BEGIN
    DECLARE estoque_disponivel INT DEFAULT 0;
    DECLARE nome_prato VARCHAR(100);
    DECLARE diferenca_quantidade INT;
    
    -- Calcular diferença na quantidade (se aumentou)
    SET diferenca_quantidade = NEW.Quantidade - OLD.Quantidade;
    
    -- Só verificar se a quantidade aumentou
    IF diferenca_quantidade > 0 THEN
        -- Buscar o estoque disponível do prato
        SELECT Estoque, Nome
        INTO estoque_disponivel, nome_prato
        FROM prato 
        WHERE ID_Prato = NEW.ID_Prato_FK;
        
        -- Verificar se há estoque suficiente para o aumento
        IF diferenca_quantidade > estoque_disponivel THEN
            SIGNAL SQLSTATE '45000' 
            SET MESSAGE_TEXT = CONCAT('Estoque insuficiente para aumentar quantidade. Estoque disponível: ', estoque_disponivel, ' para o prato: ', nome_prato);
        END IF;
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Atualizar estoque após inserir item no pedido
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_atualizar_estoque_item_insert //

CREATE TRIGGER tr_atualizar_estoque_item_insert
AFTER INSERT ON item
FOR EACH ROW
BEGIN
    -- Verificar se o pedido está aceito antes de decrementar estoque
    DECLARE status_pedido VARCHAR(255);
    
    SELECT status INTO status_pedido
    FROM pedido 
    WHERE ID_Pedido = NEW.ID_Pedido_FK;
    
    -- Só decrementar estoque se o pedido estiver aceito
    IF status_pedido = 'ACEITO' THEN
        UPDATE prato 
        SET Estoque = Estoque - NEW.Quantidade
        WHERE ID_Prato = NEW.ID_Prato_FK;
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Atualizar disponibilidade do prato baseado no estoque
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_atualizar_disponibilidade_estoque //

CREATE TRIGGER tr_atualizar_disponibilidade_estoque
AFTER UPDATE ON prato
FOR EACH ROW
BEGIN
    -- Se o estoque chegou a 0, marcar como indisponível
    IF NEW.Estoque = 0 AND OLD.Estoque > 0 THEN
        UPDATE prato 
        SET StatusDisponibilidade = 0
        WHERE ID_Prato = NEW.ID_Prato;
    END IF;
    
    -- Se o estoque voltou a ter itens, marcar como disponível
    IF NEW.Estoque > 0 AND OLD.Estoque = 0 THEN
        UPDATE prato 
        SET StatusDisponibilidade = 1
        WHERE ID_Prato = NEW.ID_Prato;
    END IF;
END //

DROP TRIGGER IF EXISTS tr_gerenciar_estoque_status_pedido //

CREATE TRIGGER tr_gerenciar_estoque_status_pedido
AFTER UPDATE ON pedido
FOR EACH ROW
BEGIN
    -- DECREMENTA o estoque quando o restaurante ACEITA o pedido
    IF NEW.status IN ('ACEITO', 'Em preparação') AND OLD.status NOT IN ('ACEITO', 'Em preparação') THEN
        UPDATE prato p
        JOIN item i ON p.ID_Prato = i.ID_Prato_FK
        SET p.Estoque = p.Estoque - i.Quantidade
        WHERE i.ID_Pedido_FK = NEW.ID_Pedido;
    END IF;
    
    -- INCREMENTA o estoque (devolve os itens) se um pedido previamente aceito for CANCELADO
    IF NEW.status = 'CANCELADO' AND OLD.status IN ('ACEITO', 'Em preparação') THEN
        UPDATE prato p
        JOIN item i ON p.ID_Prato = i.ID_Prato_FK
        SET p.Estoque = p.Estoque + i.Quantidade
        WHERE i.ID_Pedido_FK = NEW.ID_Pedido;
    END IF;
END //

DELIMITER;

-- ===============================================================
-- STORED PROCEDURES
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- PROCEDURE: Calcular total de um pedido
-- ---------------------------------------------------------------
DROP PROCEDURE IF EXISTS calcular_total_pedido //

CREATE PROCEDURE calcular_total_pedido(
    IN pedido_id CHAR(36), 
    OUT total DOUBLE
)
BEGIN
    DECLARE item_quantidade INT;
    DECLARE item_preco DOUBLE;
    DECLARE pedido_total DOUBLE DEFAULT 0;

    -- Cursor para iterar sobre os itens do pedido
    DECLARE item_cursor CURSOR FOR
        SELECT i.Quantidade, pr.Preco
        FROM item i
        JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
        WHERE i.ID_Pedido_FK = pedido_id;

    -- Handler para encerrar o cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET item_quantidade = NULL;

    -- Abrir o cursor
    OPEN item_cursor;

    -- Iterar sobre os itens do pedido e calcular o total
    item_loop: LOOP
        FETCH item_cursor INTO item_quantidade, item_preco;
        IF item_quantidade IS NULL THEN
            LEAVE item_loop;
        END IF;
        SET pedido_total = pedido_total + (item_quantidade * item_preco);
    END LOOP;

    -- Fechar o cursor
    CLOSE item_cursor;

    -- Retornar o total do pedido
    SET total = pedido_total;
END //

-- ---------------------------------------------------------------
-- PROCEDURE: Obter pedidos pendentes do restaurante com totais calculados
-- ---------------------------------------------------------------
DELIMITER //
DROP PROCEDURE IF EXISTS obter_pedidos_restaurante //

CREATE PROCEDURE obter_pedidos_restaurante(
    IN restaurante_id CHAR(36)
)
BEGIN
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
    WHERE p.status = 'PENDENTE' AND pr.ID_Restaurante_FK = restaurante_id;
END //

DELIMITER ;

-- ===============================================================
-- TRIGGER PARA CONTROLE AUTOMÁTICO DE DISPONIBILIDADE POR ESTOQUE
-- Data: 28/09/2025
-- Descrição: Atualiza automaticamente StatusDisponibilidade baseado no estoque
-- ===============================================================

DELIMITER //

CREATE TRIGGER tr_atualizar_status_por_estoque
BEFORE UPDATE ON prato
FOR EACH ROW
BEGIN
    -- Se o estoque chegou a 0, desativar o prato
    IF NEW.Estoque = 0 THEN
        SET NEW.StatusDisponibilidade = 0;
    END IF;
    
    -- Se o estoque voltou a ser > 0 e o prato estava inativo por estoque, reativar
    IF NEW.Estoque > 0 AND OLD.Estoque = 0 AND OLD.StatusDisponibilidade = 0 THEN
        SET NEW.StatusDisponibilidade = 1;
    END IF;
END//

DELIMITER ;