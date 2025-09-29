-- Adicionar campo de observações na tabela pedido
-- Este campo permitirá que clientes deixem instruções especiais para seus pedidos

ALTER TABLE `pedido` 
ADD COLUMN `observacoes` TEXT DEFAULT NULL 
AFTER `status`;

-- Comentário sobre o novo campo
-- observacoes: Campo de texto livre onde clientes podem deixar instruções especiais
-- como "sem cebola", "bem passado", "sem glúten", "entrega no portão", etc.
-- Permite até 65.535 caracteres (TEXT type)