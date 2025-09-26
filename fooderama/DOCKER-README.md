# Fooderama - Execução com Docker 🐳

Este documento explica como executar a aplicação Fooderama usando Docker e Docker Compose.

## Pré-requisitos

- Docker Desktop instalado (versão 20.10 ou superior)
- Docker Compose (incluído no Docker Desktop)

## Arquitetura da Aplicação

A aplicação Fooderama é composta por três serviços principais:

- **web**: Aplicação Flask (Python) na porta 5000
- **db**: Banco de dados MySQL 8.0 na porta 3306
- **adminer**: Interface web para administração do banco na porta 8080

## Como Executar

### 1. Clone o repositório e navegue até a pasta da aplicação:

```bash
cd fooderama
```

### 2. Configure as variáveis de ambiente:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env e altere as senhas padrão
# Especialmente importante alterar:
# - SECRET_KEY
# - DB_PASSWORD
# - MYSQL_ROOT_PASSWORD
# - MYSQL_PASSWORD
```

### 3. Execute a aplicação com Docker Compose:

```bash
docker-compose up -d
```

Este comando irá:

- Construir a imagem da aplicação Flask
- Baixar a imagem do MySQL 8.0
- Baixar a imagem do Adminer
- Criar e inicializar o banco de dados com os scripts SQL
- Iniciar todos os serviços em background

### 4. Acesse a aplicação:

- **Aplicação Principal**: http://localhost:5000
- **Adminer (Admin do Banco)**: http://localhost:8080

## Comandos Úteis

### Verificar status dos containers:

```bash
docker compose ps
```

### Ver logs da aplicação:

```bash
docker compose logs web
```

### Ver logs do banco de dados:

```bash
docker compose logs db
```

### Parar a aplicação:

```bash
docker compose down
```

### Parar e remover volumes (apaga dados do banco):

```bash
docker compose down -v
```

### Reconstruir a aplicação após mudanças no código:

```bash
docker compose build web
docker compose up -d
```

## Configurações

### Variáveis de Ambiente

⚠️ **IMPORTANTE**: Todas as configurações sensíveis agora estão no arquivo `.env` e são carregadas automaticamente pelo docker-compose.

Use o arquivo `.env.example` como base e configure suas próprias credenciais:

- `SECRET_KEY`: Chave secreta do Flask (ALTERE em produção!)
- `DB_HOST`: Host do banco de dados (padrão: db)
- `DB_USER`: Usuário do banco (padrão: root)
- `DB_PASSWORD`: Senha do banco (ALTERE em produção!)
- `DB_NAME`: Nome do banco (padrão: fooderama)
- `MYSQL_ROOT_PASSWORD`: Senha root do MySQL (ALTERE em produção!)
- `MYSQL_USER`: Usuário adicional do MySQL
- `MYSQL_PASSWORD`: Senha do usuário adicional (ALTERE em produção!)

### Portas Utilizadas

- **5000**: Aplicação Flask
- **3306**: MySQL (apenas para conexões externas)
- **8080**: Adminer (administração do banco)

## Banco de Dados

O banco de dados é inicializado automaticamente na primeira execução com os seguintes scripts SQL (executados em ordem):

1. **`01-fooderama-structure.sql`** - Criação de todas as tabelas e estrutura
2. **`02-tipos-prato-data.sql`** - Inserção dos tipos de prato iniciais (Pizza, Japonesa, etc.)
3. **`03-funcionalidades-fooderama.sql`** - Triggers, procedures e views
4. **`99-teste-inicializacao.sql`** - Verificação se tudo foi criado corretamente

### ✅ Verificar Inicialização:

Após executar `docker compose up -d`, você pode verificar se o banco foi inicializado corretamente:

1. **Acesse o Adminer**: http://localhost:8080
2. **Execute esta query** para verificar:

```sql
-- Verificar tabelas criadas
SHOW TABLES;

-- Verificar tipos de prato inseridos
SELECT * FROM tipo_prato;

-- Verificar triggers criados
SHOW TRIGGERS;
```

### 🔧 Solução se a Inicialização Falhar:

Se as tabelas não foram criadas, execute:

```bash
# Parar e remover tudo (APAGA DADOS!)
docker compose down -v

# Subir novamente (irá executar scripts de inicialização)
docker compose up -d

# Verificar logs
docker compose logs db
```

Os dados são persistidos no volume Docker `mysql_data`.

## Como Usar o Adminer para Testes

### Acessando o Adminer:

1. **Abra o navegador**: http://localhost:8080
2. **Preencha os dados de conexão**:
   - **Sistema**: MySQL
   - **Servidor**: `db` (nome do container)
   - **Usuário**: `root` (ou conforme seu .env)
   - **Senha**: Conforme configurado no seu `.env`
   - **Base de dados**: `fooderama`

### Principais Funcionalidades para Teste:

#### 1. **Visualizar Dados**:

- Clique em "fooderama" no menu lateral
- Explore as tabelas: `cliente`, `restaurante`, `prato`, `pedido`, etc.
- Clique em qualquer tabela para ver os dados

#### 2. **Executar Consultas SQL**:

- Clique em "Comando SQL" no menu
- Execute queries para testar:

```sql
-- Ver todos os clientes
SELECT * FROM cliente;

-- Ver restaurantes por tipo de comida
SELECT r.Nome_Restaurante, tp.Tipo
FROM restaurante r
JOIN tipo_prato tp ON r.ID_TipoPrato_FK = tp.ID_TipoPrato;

-- Ver pedidos com detalhes
SELECT p.*, c.Nome, r.Nome_Restaurante
FROM pedido p
JOIN cliente c ON p.ID_Cliente_FK = c.ID_Cliente
JOIN restaurante r ON p.ID_Restaurante_FK = r.ID_Restaurante;
```

#### 3. **Inserir Dados de Teste**:

```sql
-- Inserir um cliente teste
INSERT INTO cliente (ID_Cliente, CPF, Email, Senha, Telefone, Nome, Sobrenome)
VALUES (UUID(), 12345678901, 'teste@email.com', 'senha123', 11999999999, 'João', 'Silva');

-- Inserir um restaurante teste
INSERT INTO restaurante (ID_Restaurante, CNPJ, Email, Senha, Telefone, Nome_Restaurante, ID_TipoPrato_FK)
VALUES (UUID(), 12345678000199, 'restaurante@email.com', 'senha123', 11888888888, 'Restaurante Teste',
        (SELECT ID_TipoPrato FROM tipo_prato WHERE Tipo = 'Comida Caseira' LIMIT 1));
```

#### 4. **Verificar Integridade dos Dados**:

- Use o Adminer para verificar se os dados inseridos pela aplicação Flask estão corretos
- Confirme relacionamentos entre tabelas
- Valide constraints e foreign keys

#### 5. **Backup e Restore**:

- **Exportar**: Clique em "Exportar" para fazer backup
- **Importar**: Use "Importar" para restaurar dados

### Dicas de Teste:

1. **Após cadastrar via Flask**: Verifique no Adminer se os dados foram salvos
2. **Teste de relacionamentos**: Confirme se foreign keys estão funcionando
3. **Validação de dados**: Verifique se validações do Python estão refletindo no banco
4. **Performance**: Use "Explain" nas queries para analisar performance

### Vantagens do Adminer vs phpMyAdmin:

✅ **Mais leve** - Apenas 1 arquivo PHP  
✅ **Interface mais limpa** - Foco na funcionalidade  
✅ **Suporte multi-banco** - MySQL, PostgreSQL, SQLite, etc.  
✅ **Melhor para desenvolvimento** - Interface mais direta  
✅ **Menos recursos** - Consome menos memória

## Desenvolvimento

### Para desenvolvimento local:

1. Modifique o código
2. Reconstrua o container:

```bash
docker-compose build web
docker-compose up -d
```

### Para acessar o container da aplicação:

```bash
docker-compose exec web bash
```

### Para acessar o MySQL diretamente:

```bash
docker-compose exec db mysql -u root -p fooderama
```

## Solução de Problemas

### Container não inicia:

- Verifique se as portas 5000, 3306 e 8080 não estão sendo usadas
- Execute: `docker-compose logs [nome-do-servico]`

### Erro de conexão com banco:

- Aguarde alguns segundos para o MySQL inicializar completamente
- Verifique os logs: `docker-compose logs db`

### Resetar completamente a aplicação:

```bash
docker-compose down -v
docker-compose up -d
```

## Estrutura dos Arquivos Docker

```
fooderama/
├── Dockerfile                 # Imagem da aplicação Flask
├── docker-compose.yml         # Orquestração dos serviços
├── .dockerignore              # Arquivos ignorados no build
├── .env                       # Variáveis de ambiente (NÃO versionar!)
├── .env.example               # Template de variáveis de ambiente
├── TESTE-GUIDE.md             # Guia de testes com Adminer
└── BANDO DE DADOS/            # Scripts SQL de inicialização (executados em ordem)
    ├── 01-fooderama-structure.sql      # Estrutura das tabelas
    ├── 02-tipos-prato-data.sql         # Dados iniciais (tipos de prato)
    ├── 03-funcionalidades-fooderama.sql # Triggers, procedures e views
    ├── 99-teste-inicializacao.sql      # Verificação da inicialização
    ├── fooderama.sql                   # [ORIGINAL - não usado]
    ├── funcionalidades_fooderama.sql   # [ORIGINAL - não usado]
    └── inserir_tipos_prato.sql         # [ORIGINAL - não usado]
```

## Segurança

⚠️ **CRÍTICO**:

1. **NUNCA** commite o arquivo `.env` com credenciais reais
2. Use o `.env.example` como template e crie seu próprio `.env`
3. Em produção, gere senhas fortes e únicas para:
   - `SECRET_KEY` (use pelo menos 32 caracteres aleatórios)
   - `DB_PASSWORD`
   - `MYSQL_ROOT_PASSWORD`
   - `MYSQL_PASSWORD`

### Exemplo de geração de chave segura:

```bash
# Gerar SECRET_KEY segura (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Suporte

Para problemas ou dúvidas sobre a execução com Docker, verifique:

1. Logs dos containers
2. Status dos serviços
3. Conectividade de rede entre containers
