-- Script para adicionar campo de observações na tabela pedido
-- Execute este script no banco de dados para adicionar o campo observações
DELIMITER //

ALTER TABLE `pedido` 
ADD COLUMN `observacoes` TEXT NULL AFTER `status`;

-- Verificar se a coluna foi adicionada corretamente
DESCRIBE `pedido`;
DELIMITER ;
