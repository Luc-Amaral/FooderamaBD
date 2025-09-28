-- ===============================================================
-- CONFIGURAÇÃO DE ISOLAMENTO TRANSACIONAL
-- ===============================================================
-- Arquivo: 04-isolamento-transacional.sql
-- Objetivo: Evitar problemas de concorrência em transações simultâneas
-- Nível: READ COMMITTED para balancear consistência e performance
-- ===============================================================

USE fooderama;

-- ===============================================================
-- CONFIGURAÇÃO GLOBAL DE ISOLAMENTO
-- ===============================================================

-- Definir nível de isolamento padrão como READ COMMITTED
-- Isso garante que transações não vejam dados não commitados
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET GLOBAL TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- ===============================================================
-- PROCEDURE PARA ACEITAR PEDIDO COM PROTEÇÃO TRANSACIONAL
-- ===============================================================

DELIMITER //

DROP PROCEDURE IF EXISTS sp_aceitar_pedido_seguro //

CREATE PROCEDURE sp_aceitar_pedido_seguro(
    IN p_pedido_id CHAR(36)
)
BEGIN
    DECLARE v_erro VARCHAR(255) DEFAULT '';
    DECLARE v_estoque_insuficiente INT DEFAULT 0;
    DECLARE v_pedido_status VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    -- Iniciar transação com nível de isolamento explícito
    SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
    START TRANSACTION;
    
    -- Verificar se o pedido existe e está pendente
    SELECT status INTO v_pedido_status
    FROM pedido 
    WHERE ID_Pedido = p_pedido_id
    FOR UPDATE; -- Lock pessimista para evitar modificações concorrentes
    
    IF v_pedido_status IS NULL THEN
        SET v_erro = 'Pedido não encontrado';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido não encontrado';
    END IF;
    
    IF v_pedido_status != 'PENDENTE' THEN
        SET v_erro = CONCAT('Pedido já está com status: ', v_pedido_status);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_erro;
    END IF;
    
    -- Verificar estoque disponível para todos os itens do pedido
    -- Usando SELECT FOR UPDATE para lock dos registros
    SELECT COUNT(*) INTO v_estoque_insuficiente
    FROM item i
    INNER JOIN prato p ON i.ID_Prato_FK = p.ID_Prato
    WHERE i.ID_Pedido_FK = p_pedido_id 
    AND p.Estoque < i.Quantidade
    FOR UPDATE;
    
    IF v_estoque_insuficiente > 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estoque insuficiente para um ou mais itens do pedido';
    END IF;
    
    -- Atualizar estoque com lock otimista
    UPDATE prato p
    INNER JOIN item i ON p.ID_Prato = i.ID_Prato_FK
    SET p.Estoque = p.Estoque - i.Quantidade
    WHERE i.ID_Pedido_FK = p_pedido_id
    AND p.Estoque >= i.Quantidade; -- Verificação adicional no momento da atualização
    
    -- Verificar se todas as atualizações foram bem-sucedidas
    IF ROW_COUNT() = 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Falha ao atualizar estoque - possível concorrência detectada';
    END IF;
    
    -- Atualizar status do pedido
    UPDATE pedido 
    SET status = 'ACEITO'
    WHERE ID_Pedido = p_pedido_id;
    
    -- Confirmar transação
    COMMIT;
    
END //

DELIMITER ;

-- ===============================================================
-- CONFIGURAÇÕES ADICIONAIS DE SEGURANÇA
-- ===============================================================

-- Configurar timeout para locks (evitar deadlocks prolongados)
SET SESSION innodb_lock_wait_timeout = 10;
SET GLOBAL innodb_lock_wait_timeout = 10;

-- Configurar deadlock detection (MySQL detecta e resolve automaticamente)
SET GLOBAL innodb_deadlock_detect = ON;

-- ===============================================================
-- PROCEDURE PARA VERIFICAÇÃO DE ESTOQUE EM TEMPO REAL
-- ===============================================================

DELIMITER //

DROP PROCEDURE IF EXISTS sp_verificar_estoque_disponivel //

CREATE PROCEDURE sp_verificar_estoque_disponivel(
    IN p_prato_id CHAR(36),
    IN p_quantidade INT,
    OUT p_disponivel BOOLEAN
)
BEGIN
    DECLARE v_estoque_atual INT DEFAULT 0;
    
    -- Usar SELECT FOR SHARE para verificação não bloqueante
    SELECT Estoque INTO v_estoque_atual
    FROM prato 
    WHERE ID_Prato = p_prato_id 
    AND StatusDisponibilidade = 1
    LOCK IN SHARE MODE;
    
    IF v_estoque_atual >= p_quantidade THEN
        SET p_disponivel = TRUE;
    ELSE
        SET p_disponivel = FALSE;
    END IF;
    
END //

DELIMITER ;

-- ===============================================================
-- ÍNDICES PARA OTIMIZAR CONSULTAS CONCORRENTES
-- ===============================================================

-- Índice composto para otimizar verificações de pedido
CREATE INDEX idx_pedido_status_data 
ON pedido (status, Data);

-- Índice para otimizar consultas de estoque  
CREATE INDEX idx_prato_estoque_status 
ON prato (Estoque, StatusDisponibilidade);

-- Índice para otimizar consultas de itens por pedido
CREATE INDEX idx_item_pedido_prato 
ON item (ID_Pedido_FK, ID_Prato_FK);

