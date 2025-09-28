# 🍕 Fooderama - Sistema de Delivery

Sistema completo de delivery de comida desenvolvido com Flask e MySQL, incluindo gestão de estoque automatizada e proteção contra transações concorrentes.

## 🚀 Setup Rápido

### Pré-requisitos

- Docker e Docker Compose instalados
- Git instalado

### 🔧 Instalação

1. **Clone o repositório:**

```bash
git clone <seu-repositorio>
cd Fooderama/fooderama
```

2. **Execute com Docker:**

```bash
docker-compose up -d
```

3. **Acesse a aplicação:**

- **Website:** http://localhost:5000
- **Adminer (DB):** http://localhost:8080
  - Servidor: `db`
  - Usuário: `root`
  - Senha: `root`
  - Base de dados: `fooderama`

## 📋 Funcionalidades

### ✅ **Sistema Completo:**

- 🏪 **Cadastro de Restaurantes** - Registro e login de estabelecimentos
- 👤 **Cadastro de Clientes** - Registro e login de usuários
- 🍽️ **Gestão de Pratos** - CRUD completo com controle de estoque
- 🛒 **Sistema de Pedidos** - Carrinho, checkout e acompanhamento
- 💳 **Pagamentos** - Suporte a PIX, cartão de débito/crédito
- 📍 **Endereços** - Gestão de endereços de entrega

### 🔒 **Proteções Avançadas:**

- **Gestão automática de estoque** - Decremento ao aceitar pedidos
- **Status automático** - Produtos indisponíveis quando estoque = 0
- **Isolamento transacional** - Proteção contra condições de corrida
- **Triggers MySQL** - Automação de regras de negócio

## 🗃️ Estrutura do Banco

O banco é inicializado automaticamente com:

1. **01-fooderama-structure.sql** - Estrutura das tabelas
2. **02-tipos-prato-data.sql** - Tipos de comida (Pizza, Lanche, etc.)
3. **03-funcionalidades-fooderama.sql** - Triggers automáticos
4. **04-isolamento-transacional.sql** - Proteção transacional
5. **99-teste-inicializacao.sql** - Dados de teste

## 🔧 Desenvolvimento

### Estrutura de Arquivos:

```
fooderama/
├── app/
│   ├── routes.py          # Rotas da aplicação
│   ├── db_config.py       # Configuração do banco
│   └── templates/         # Templates HTML
├── BANDO DE DADOS/        # Scripts SQL de inicialização
├── docker-compose.yml     # Configuração Docker
├── requirements.txt       # Dependências Python
└── Dockerfile            # Imagem da aplicação
```

### Comandos Úteis:

```bash
# Ver logs da aplicação
docker-compose logs -f web

# Acessar banco de dados
docker-compose exec db mysql -u root -proot fooderama

# Reiniciar serviços
docker-compose restart

# Parar tudo
docker-compose down

# Rebuild completo
docker-compose down && docker-compose up -d --build
```

## 📊 Recursos Técnicos

- **Backend:** Flask 2.3.3 com Flask-Login
- **Banco:** MySQL 8.0 com triggers automáticos
- **Frontend:** HTML5, CSS3, JavaScript, Tailwind CSS
- **Container:** Docker com healthcheck
- **Isolamento:** READ COMMITTED para concorrência
- **Arquitetura:** MVC com separação de responsabilidades

---

**🎯 Objetivo:** Lab. Banco de Dados - UFMT  
**⚡ Status:** Pronto para produção com Docker
