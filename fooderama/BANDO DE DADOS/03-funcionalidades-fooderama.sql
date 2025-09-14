-- ===============================================================
-- INICIALIZAÇÃO DO BANCO FOODERAMA - PARTE 3: FUNCIONALIDADES
-- Arquivo: 03-funcionalidades-fooderama.sql
-- Descrição: Triggers, funções e procedimentos para o sistema
-- ===============================================================

USE fooderama;

-- ===============================================================
-- TRIGGERS DE VALIDAÇÃO E AUDITORIA
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- TRIGGER: Validação de dados do cliente antes da inserção
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_validar_cliente_insert //

CREATE TRIGGER tr_validar_cliente_insert
BEFORE INSERT ON cliente
FOR EACH ROW
BEGIN
    -- Validar formato do email
    IF NEW.Email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Validar CPF (11 dígitos)
    IF LENGTH(NEW.CPF) != 11 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'CPF deve ter exatamente 11 dígitos';
    END IF;
    
    -- Validar telefone (10 ou 11 dígitos)
    IF LENGTH(NEW.Telefone) NOT IN (10, 11) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Telefone deve ter 10 ou 11 dígitos';
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Validação de dados do restaurante antes da inserção
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_validar_restaurante_insert //

CREATE TRIGGER tr_validar_restaurante_insert
BEFORE INSERT ON restaurante
FOR EACH ROW
BEGIN
    -- Validar formato do email
    IF NEW.Email NOT REGEXP '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,4}$' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Formato de email inválido';
    END IF;
    
    -- Validar CNPJ (14 dígitos)
    IF LENGTH(NEW.CNPJ) != 14 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'CNPJ deve ter exatamente 14 dígitos';
    END IF;
    
    -- Validar telefone (10 ou 11 dígitos)
    IF LENGTH(NEW.Telefone) NOT IN (10, 11) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Telefone deve ter 10 ou 11 dígitos';
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Validação do preço do prato
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_validar_prato_preco //

CREATE TRIGGER tr_validar_prato_preco
BEFORE INSERT ON prato
FOR EACH ROW
BEGIN
    -- Validar se o preço é positivo
    IF NEW.Preco <= 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'O preço do prato deve ser maior que zero';
    END IF;
    
    -- Validar se o preço não é absurdamente alto (mais de R$ 1000)
    IF NEW.Preco > 1000.00 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'O preço do prato não pode exceder R$ 1000,00';
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Atualizar valor total do pedido automaticamente
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_atualizar_valor_pedido //

CREATE TRIGGER tr_atualizar_valor_pedido
BEFORE INSERT ON pedido
FOR EACH ROW
BEGIN
    DECLARE preco_prato DECIMAL(10,2);
    
    -- Buscar o preço do prato
    SELECT Preco INTO preco_prato
    FROM prato 
    WHERE ID_Prato = NEW.ID_Prato_FK;
    
    -- Definir o valor total como o preço do prato
    SET NEW.Valor_Total = preco_prato;
    
    -- Definir a data do pedido como agora se não foi fornecida
    IF NEW.Data_Pedido IS NULL THEN
        SET NEW.Data_Pedido = NOW();
    END IF;
    
    -- Definir status padrão se não foi fornecido
    IF NEW.Status_Pedido IS NULL OR NEW.Status_Pedido = '' THEN
        SET NEW.Status_Pedido = 'Pendente';
    END IF;
END //

-- ---------------------------------------------------------------
-- TRIGGER: Validação da nota de avaliação
-- ---------------------------------------------------------------
DROP TRIGGER IF EXISTS tr_validar_avaliacao //

CREATE TRIGGER tr_validar_avaliacao
BEFORE INSERT ON avaliacao
FOR EACH ROW
BEGIN
    -- Validar se a nota está entre 1 e 5
    IF NEW.Nota < 1 OR NEW.Nota > 5 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'A nota da avaliação deve estar entre 1 e 5';
    END IF;
    
    -- Definir a data da avaliação como agora se não foi fornecida
    IF NEW.Data_Avaliacao IS NULL THEN
        SET NEW.Data_Avaliacao = NOW();
    END IF;
END //

DELIMITER ;

-- ===============================================================
-- STORED PROCEDURES
-- ===============================================================

DELIMITER //

-- ---------------------------------------------------------------
-- PROCEDURE: Buscar restaurantes por tipo de comida
-- ---------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_buscar_restaurantes_por_tipo //

CREATE PROCEDURE sp_buscar_restaurantes_por_tipo(
    IN p_tipo_comida VARCHAR(30)
)
BEGIN
    SELECT 
        r.ID_Restaurante,
        r.Nome_Restaurante,
        r.Email,
        r.Telefone,
        tp.Tipo as Tipo_Comida,
        COUNT(p.ID_Prato) as Total_Pratos,
        COALESCE(AVG(a.Nota), 0) as Media_Avaliacoes
    FROM restaurante r
    JOIN tipo_prato tp ON r.ID_TipoPrato_FK = tp.ID_TipoPrato
    LEFT JOIN prato p ON r.ID_Restaurante = p.ID_Restaurante_FK
    LEFT JOIN avaliacao a ON r.ID_Restaurante = a.ID_Restaurante_FK
    WHERE tp.Tipo LIKE CONCAT('%', p_tipo_comida, '%')
    GROUP BY r.ID_Restaurante, r.Nome_Restaurante, r.Email, r.Telefone, tp.Tipo
    ORDER BY Media_Avaliacoes DESC, Total_Pratos DESC;
END //

-- ---------------------------------------------------------------
-- PROCEDURE: Obter histórico de pedidos de um cliente
-- ---------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_historico_cliente //

CREATE PROCEDURE sp_historico_cliente(
    IN p_cliente_id CHAR(36)
)
BEGIN
    SELECT 
        p.ID_Pedido,
        p.Data_Pedido,
        p.Status_Pedido,
        p.Valor_Total,
        r.Nome_Restaurante,
        pr.Nome_Prato,
        pr.Preco
    FROM pedido p
    JOIN restaurante r ON p.ID_Restaurante_FK = r.ID_Restaurante
    JOIN prato pr ON p.ID_Prato_FK = pr.ID_Prato
    WHERE p.ID_Cliente_FK = p_cliente_id
    ORDER BY p.Data_Pedido DESC;
END //

-- ---------------------------------------------------------------
-- PROCEDURE: Obter estatísticas de um restaurante
-- ---------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_estatisticas_restaurante //

CREATE PROCEDURE sp_estatisticas_restaurante(
    IN p_restaurante_id CHAR(36)
)
BEGIN
    SELECT 
        r.Nome_Restaurante,
        COUNT(DISTINCT p.ID_Pedido) as Total_Pedidos,
        COUNT(DISTINCT pr.ID_Prato) as Total_Pratos,
        COALESCE(SUM(p.Valor_Total), 0) as Receita_Total,
        COALESCE(AVG(a.Nota), 0) as Media_Avaliacoes,
        COUNT(DISTINCT a.ID_Avaliacao) as Total_Avaliacoes
    FROM restaurante r
    LEFT JOIN pedido p ON r.ID_Restaurante = p.ID_Restaurante_FK
    LEFT JOIN prato pr ON r.ID_Restaurante = pr.ID_Restaurante_FK
    LEFT JOIN avaliacao a ON r.ID_Restaurante = a.ID_Restaurante_FK
    WHERE r.ID_Restaurante = p_restaurante_id
    GROUP BY r.ID_Restaurante, r.Nome_Restaurante;
END //

DELIMITER ;

-- ===============================================================
-- VIEWS ÚTEIS
-- ===============================================================

-- ---------------------------------------------------------------
-- VIEW: Resumo de restaurantes com estatísticas
-- ---------------------------------------------------------------
CREATE OR REPLACE VIEW vw_restaurantes_resumo AS
SELECT 
    r.ID_Restaurante,
    r.Nome_Restaurante,
    r.Email,
    r.Telefone,
    tp.Tipo as Tipo_Comida,
    COUNT(DISTINCT p.ID_Prato) as Total_Pratos,
    COUNT(DISTINCT ped.ID_Pedido) as Total_Pedidos,
    COALESCE(AVG(a.Nota), 0) as Media_Avaliacoes,
    COALESCE(SUM(ped.Valor_Total), 0) as Receita_Total
FROM restaurante r
JOIN tipo_prato tp ON r.ID_TipoPrato_FK = tp.ID_TipoPrato
LEFT JOIN prato p ON r.ID_Restaurante = p.ID_Restaurante_FK
LEFT JOIN pedido ped ON r.ID_Restaurante = ped.ID_Restaurante_FK
LEFT JOIN avaliacao a ON r.ID_Restaurante = a.ID_Restaurante_FK
GROUP BY r.ID_Restaurante, r.Nome_Restaurante, r.Email, r.Telefone, tp.Tipo;

-- ---------------------------------------------------------------
-- VIEW: Pedidos com informações completas
-- ---------------------------------------------------------------
CREATE OR REPLACE VIEW vw_pedidos_completos AS
SELECT 
    p.ID_Pedido,
    p.Data_Pedido,
    p.Status_Pedido,
    p.Valor_Total,
    c.Nome as Cliente_Nome,
    c.Email as Cliente_Email,
    r.Nome_Restaurante,
    pr.Nome_Prato,
    pr.Preco as Preco_Prato,
    tp.Tipo as Tipo_Comida
FROM pedido p
JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
JOIN restaurante r ON p.ID_Restaurante_FK = r.ID_Restaurante
JOIN prato pr ON p.ID_Prato_FK = pr.ID_Prato
JOIN tipo_prato tp ON r.ID_TipoPrato_FK = tp.ID_TipoPrato;

-- Funcionalidades avançadas criadas com sucesso!
SELECT 'Triggers, procedures e views criados com sucesso!' as status;