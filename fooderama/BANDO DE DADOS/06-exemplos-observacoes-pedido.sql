-- Exemplos de uso do campo de observações em pedidos
-- Execute após aplicar o script 05-adicionar-observacoes-pedido.sql

-- Exemplo 1: Inserir um pedido com observações específicas de preparo
INSERT INTO pedido (ID_Pedido, ID_Cliente_FK, ID_Endereco_FK, ID_MetodoPagamento_FK, Data, Hora, status, observacoes)
VALUES (
    UUID(),
    'cliente-id-exemplo',
    'endereco-id-exemplo',
    'pagamento-id-exemplo',
    CURDATE(),
    CURTIME(),
    'PENDENTE',
    'Sem cebola no hambúrguer, batata bem crocante e refrigerante sem gelo'
);

-- Exemplo 2: Inserir um pedido com observações de entrega
INSERT INTO pedido (ID_Pedido, ID_Cliente_FK, ID_Endereco_FK, ID_MetodoPagamento_FK, Data, Hora, status, observacoes)
VALUES (
    UUID(),
    'cliente-id-exemplo-2',
    'endereco-id-exemplo-2',
    'pagamento-id-exemplo-2',
    CURDATE(),
    CURTIME(),
    'PENDENTE',
    'Entregar no portão principal, tocar a campainha duas vezes. Pizza bem assada.'
);

-- Exemplo 3: Consultar pedidos com observações específicas
-- Buscar pedidos com observações relacionadas a alergias ou restrições
SELECT 
    p.ID_Pedido,
    p.Data,
    p.Hora,
    p.status,
    p.observacoes,
    c.Nome as cliente_nome
FROM pedido p
JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
WHERE p.observacoes LIKE '%sem%' 
   OR p.observacoes LIKE '%alergia%' 
   OR p.observacoes LIKE '%glúten%'
ORDER BY p.Data DESC, p.Hora DESC;

-- Exemplo 4: Consultar todos os pedidos pendentes com observações para um restaurante
SELECT 
    p.ID_Pedido,
    c.Nome as cliente_nome,
    c.Telefone as cliente_telefone,
    p.Data,
    p.Hora,
    p.observacoes,
    GROUP_CONCAT(CONCAT(pr.Nome, ' (', i.Quantidade, 'x)') SEPARATOR ', ') as itens_pedido
FROM pedido p
JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
JOIN item i ON p.ID_Pedido = i.ID_Pedido_FK
JOIN prato pr ON i.ID_Prato_FK = pr.ID_Prato
WHERE p.status = 'PENDENTE' 
  AND pr.ID_Restaurante_FK = 'id-do-restaurante'
  AND p.observacoes IS NOT NULL 
  AND p.observacoes != ''
GROUP BY p.ID_Pedido, c.Nome, c.Telefone, p.Data, p.Hora, p.observacoes
ORDER BY p.Data DESC, p.Hora DESC;

-- Exemplo 5: Atualizar observações de um pedido existente (caso necessário)
UPDATE pedido 
SET observacoes = 'Observações atualizadas: sem pimenta, extra queijo'
WHERE ID_Pedido = 'id-do-pedido-exemplo';

-- Exemplo 6: Buscar estatísticas de pedidos com observações
SELECT 
    COUNT(*) as total_pedidos,
    COUNT(CASE WHEN observacoes IS NOT NULL AND observacoes != '' THEN 1 END) as pedidos_com_observacoes,
    ROUND(
        (COUNT(CASE WHEN observacoes IS NOT NULL AND observacoes != '' THEN 1 END) * 100.0) / COUNT(*), 
        2
    ) as percentual_com_observacoes
FROM pedido
WHERE Data >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);