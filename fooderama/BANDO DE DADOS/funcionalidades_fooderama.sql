-- ===============================================================
-- FUNCIONALIDADES AVANÇADAS DO SISTEMA FOODERAMA
-- Arquivo: funcionalidades_fooderama.sql
-- Criado em: 01/09/2025
-- Descrição: Triggers, funções e procedimentos para o sistema
-- ===============================================================

USE fooderama;

-- ===============================================================
-- TRIGGERS DE VALIDAÇÃO
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- TRIGGER: Verificação de estoque antes de inserir item no pedido
-- ---------------------------------------------------------------
CREATE OR REPLACE TRIGGER tr_verificar_estoque_item
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
CREATE OR REPLACE TRIGGER tr_verificar_estoque_item_update
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
CREATE OR REPLACE TRIGGER tr_atualizar_estoque_item_insert
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
CREATE OR REPLACE TRIGGER tr_atualizar_disponibilidade_estoque
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

DELIMITER ;

-- ===============================================================
-- FUNÇÕES AUXILIARES
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- FUNÇÃO: Verificar se há estoque suficiente para um prato
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_verificar_estoque_disponivel(
    p_id_prato CHAR(36),
    p_quantidade INT
) RETURNS BOOLEAN
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE estoque_atual INT DEFAULT 0;
    
    SELECT Estoque INTO estoque_atual
    FROM prato 
    WHERE ID_Prato = p_id_prato;
    
    RETURN (estoque_atual >= p_quantidade);
END //

-- ---------------------------------------------------------------
-- FUNÇÃO: Obter estoque atual de um prato
-- ---------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_obter_estoque_prato(
    p_id_prato CHAR(36)
) RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE estoque_atual INT DEFAULT 0;
    
    SELECT Estoque INTO estoque_atual
    FROM prato 
    WHERE ID_Prato = p_id_prato;
    
    RETURN estoque_atual;
END //

DELIMITER ;

-- ===============================================================
-- PROCEDIMENTOS ARMAZENADOS
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- PROCEDURE: Adicionar estoque a um prato
-- ---------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_adicionar_estoque(
    IN p_id_prato CHAR(36),
    IN p_quantidade INT
)
BEGIN
    DECLARE prato_existe INT DEFAULT 0;
    
    -- Verificar se o prato existe
    SELECT COUNT(*) INTO prato_existe
    FROM prato 
    WHERE ID_Prato = p_id_prato;
    
    IF prato_existe = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Prato não encontrado';
    END IF;
    
    IF p_quantidade <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Quantidade deve ser maior que zero';
    END IF;
    
    -- Adicionar ao estoque
    UPDATE prato 
    SET Estoque = Estoque + p_quantidade
    WHERE ID_Prato = p_id_prato;
    
    SELECT CONCAT('Estoque atualizado. Nova quantidade: ', (SELECT Estoque FROM prato WHERE ID_Prato = p_id_prato)) AS resultado;
END //

