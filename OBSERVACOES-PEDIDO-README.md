# Funcionalidade: Campo de Observações em Pedidos

## Descrição
Foi implementado um campo de observações nos pedidos do sistema Fooderama, permitindo que clientes deixem instruções especiais para seus pedidos e que restaurantes possam visualizar essas observações.

## Arquivos Modificados

### 1. Banco de Dados
- **05-adicionar-observacoes-pedido.sql**: Script SQL para adicionar o campo `observacoes` na tabela `pedido`
- **06-exemplos-observacoes-pedido.sql**: Exemplos de uso e consultas com o novo campo

### 2. Backend (Python/Flask)
- **app/routes/orders.py**: 
  - Função `finalizar_compra()`: Modificada para receber e salvar observações
  - Função `historico_rest()`: Modificada para retornar observações nas consultas

### 3. Frontend (HTML/CSS/JavaScript)
- **app/templates/restaurant.html**: Adicionado campo de observações no modal de checkout
- **app/templates/pratos_por_tipo.html**: Adicionado campo de observações no modal de checkout
- **app/templates/historico_rest.html**: Adicionada coluna de observações nas tabelas de pedidos
- **app/static/js/restaurant_new.js**: Modificada função `finalizarPedido()` para enviar observações
- **app/static/js/pratos_por_tipo.js**: Modificada função `finalizarPedido()` para enviar observações

## Como Funciona

### Para o Cliente:
1. Ao finalizar um pedido, o cliente encontra um campo "Observações do Pedido (opcional)"
2. Pode digitar instruções especiais como:
   - "Sem cebola"
   - "Bem passado"
   - "Extra queijo"
   - "Entregar no portão"
   - "Sem glúten"
3. O campo aceita até 500 caracteres
4. As observações são enviadas junto com o pedido

### Para o Restaurante:
1. No histórico de pedidos pendentes, as observações aparecem destacadas em uma caixa amarela
2. No histórico geral, as observações aparecem em uma caixa cinza
3. Se não há observações, aparece "Nenhuma observação"
4. O restaurante pode ver as instruções antes de aceitar ou recusar o pedido

## Estrutura do Banco de Dados

```sql
ALTER TABLE `pedido` 
ADD COLUMN `observacoes` TEXT DEFAULT NULL 
AFTER `status`;
```

### Características do campo:
- **Tipo**: TEXT (até 65.535 caracteres)
- **Obrigatório**: Não (DEFAULT NULL)
- **Posição**: Após a coluna `status`

## Interface de Usuario

### Campo de Observações (Cliente):
- Aparece no modal de finalização do pedido
- Placeholder: "Ex: sem cebola, bem passado, entregar no portão..."
- Máximo de 500 caracteres
- Redimensionamento desabilitado (resize-none)

### Visualização das Observações (Restaurante):
- **Pedidos Pendentes**: Caixa destacada em amarelo com borda amarela
- **Histórico**: Caixa cinza com borda cinza
- **Sem observações**: Texto em cinza "Nenhuma observação"

## Exemplos de Uso

### Observações Comuns:
- **Preparo**: "Sem cebola", "Bem passado", "Mal passado", "Extra queijo"
- **Alergias**: "Sem glúten", "Sem lactose", "Alérgico a amendoim"
- **Entrega**: "Entregar no portão", "Apartamento 201", "Tocar campainha duas vezes"
- **Bebidas**: "Sem gelo", "Com canudo de papel", "Bem gelado"

### Vantagens:
1. **Comunicação clara** entre cliente e restaurante
2. **Redução de erros** nos pedidos
3. **Melhora na satisfação** do cliente
4. **Facilita instruções especiais** de entrega
5. **Suporte a restrições alimentares**

## Considerações Técnicas

### Validações:
- Máximo 500 caracteres no frontend
- Campo opcional (pode estar vazio)
- Texto livre (sem validação de formato)

### Segurança:
- Não há sanitização especial necessária (texto simples)
- Campo não é obrigatório (não quebra funcionalidade existente)

### Performance:
- Campo TEXT não impacta significativamente as consultas
- Indexação não necessária (campo de texto livre)

## Instalação

1. Execute o script SQL: `05-adicionar-observacoes-pedido.sql`
2. Reinicie a aplicação Flask
3. A funcionalidade estará disponível imediatamente

## Teste da Funcionalidade

1. Acesse como cliente
2. Adicione itens ao carrinho
3. No checkout, adicione observações no campo correspondente
4. Finalize o pedido
5. Acesse como restaurante
6. Visualize o pedido pendente no histórico
7. Verifique se as observações aparecem corretamente