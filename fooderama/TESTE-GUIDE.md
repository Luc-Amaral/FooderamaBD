# Guia Rápido - Testando Fooderama com Adminer 🧪

## Comandos para Iniciar

```bash
# 1. Subir a aplicação
docker-compose up -d

# 2. Verificar se todos os serviços estão rodando
docker-compose ps

# 3. Ver logs se houver problemas
docker-compose logs web
docker-compose logs db
```

## Acessos

- **Aplicação**: http://localhost:5000
- **Adminer**: http://localhost:8080

## Login no Adminer

```
Sistema: MySQL
Servidor: db
Usuário: root
Senha: (conforme seu .env)
Base de dados: fooderama
```

## Queries Úteis para Teste

### Verificar Estrutura

```sql
-- Ver todas as tabelas
SHOW TABLES;

-- Ver estrutura de uma tabela
DESCRIBE cliente;
DESCRIBE restaurante;
DESCRIBE prato;
DESCRIBE pedido;
```

### Dados Iniciais

```sql
-- Ver tipos de prato disponíveis
SELECT * FROM tipo_prato;

-- Contar registros por tabela
SELECT 'clientes' as tabela, COUNT(*) as total FROM cliente
UNION ALL
SELECT 'restaurantes' as tabela, COUNT(*) as total FROM restaurante
UNION ALL
SELECT 'pratos' as tabela, COUNT(*) as total FROM prato
UNION ALL
SELECT 'pedidos' as tabela, COUNT(*) as total FROM pedido;
```

### Inserir Dados de Teste

```sql
-- Cliente teste
INSERT INTO cliente (ID_Cliente, CPF, Email, Senha, Telefone, Nome, Sobrenome)
VALUES (UUID(), 12345678901, 'joao@teste.com', 'senha123', 11999999999, 'João', 'Silva');

-- Restaurante teste
INSERT INTO restaurante (ID_Restaurante, CNPJ, Email, Senha, Telefone, Nome_Restaurante, ID_TipoPrato_FK)
VALUES (UUID(), 12345678000199, 'pizza@teste.com', 'senha123', 11888888888, 'Pizzaria Teste',
        (SELECT ID_TipoPrato FROM tipo_prato WHERE Tipo = 'Pizza' LIMIT 1));
```

### Consultas de Validação

```sql
-- Restaurantes por tipo de comida
SELECT tp.Tipo, COUNT(r.ID_Restaurante) as total_restaurantes
FROM tipo_prato tp
LEFT JOIN restaurante r ON tp.ID_TipoPrato = r.ID_TipoPrato_FK
GROUP BY tp.Tipo
ORDER BY total_restaurantes DESC;

-- Pedidos com detalhes completos
SELECT
    p.Data_Pedido,
    c.Nome as cliente_nome,
    r.Nome_Restaurante,
    pr.Nome_Prato,
    p.Valor_Total
FROM pedido p
JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
JOIN restaurante r ON p.ID_Restaurante_FK = r.ID_Restaurante
JOIN prato pr ON p.ID_Prato_FK = pr.ID_Prato
ORDER BY p.Data_Pedido DESC;
```

## Fluxo de Teste Recomendado

### 1. **Verificação Inicial**

```sql
-- Confirmar que as tabelas foram criadas
SHOW TABLES;

-- Verificar tipos de prato inseridos
SELECT * FROM tipo_prato;
```

### 2. **Teste de Cadastro (via Flask)**

1. Acesse http://localhost:5000
2. Cadastre um cliente
3. No Adminer: `SELECT * FROM cliente ORDER BY ID_Cliente DESC LIMIT 5;`

### 3. **Teste de Relacionamentos**

```sql
-- Verificar foreign keys funcionando
SELECT
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_SCHEMA = 'fooderama';
```

### 4. **Teste de Performance**

```sql
-- Verificar índices
SHOW INDEX FROM cliente;
SHOW INDEX FROM restaurante;
SHOW INDEX FROM pedido;
```

## Comandos Docker Úteis

```bash
# Parar tudo
docker-compose down

# Resetar banco de dados (CUIDADO: apaga todos os dados)
docker-compose down -v
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f web

# Conectar diretamente ao MySQL
docker-compose exec db mysql -u root -p fooderama

# Backup do banco
docker-compose exec db mysqldump -u root -p fooderama > backup.sql

# Restore do banco
docker-compose exec -T db mysql -u root -p fooderama < backup.sql
```

## Solução de Problemas

### Adminer não conecta:

1. Verifique se o container MySQL está rodando: `docker-compose ps`
2. Aguarde alguns segundos para o MySQL inicializar
3. Confirme as credenciais no arquivo `.env`

### Dados não aparecem:

1. Verifique logs: `docker-compose logs db`
2. Confirme se scripts SQL foram executados
3. Teste conexão: `docker-compose exec db mysql -u root -p -e "USE fooderama; SHOW TABLES;"`

### Performance lenta:

1. Verifique recursos: `docker stats`
2. Analise queries lentas no Adminer com EXPLAIN
