Sumario:(ctrl + click nos links)
[🚀 Setup Rápido](#-setup-rápido) •
[📋 Funcionalidades](#-funcionalidades) •
[🔧 Desenvolvimento](#-desenvolvimento) •
[🌐 APIs](#-apis-integradas) •
[📊 Banco de Dados](#-estrutura-do-banco)

## Requerimentos:(recomendado instalar automatico com: docker-compose up -d --build)

**Flask==3.0.0**
**Flask-CORS==4.0.1**
**Flask-Login==0.6.3**
**Werkzeug==3.0.1**
**mysql-connector-python==8.2.0**
**python-dotenv==1.0.0**
**requests==2.31.0**
**pyinstaller==6.3.0**

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Git** instalado
- **ngrok** (opcional - para acesso externo em server)

### 🔧 Instalação e Execução

1. **Clone o repositório:**

```bash
git clone -b feat/organization2 https://github.com/Luc-Amaral/FooderamaBD.git
cd FooderamaBD/fooderama
```

2. **Execute com Docker (desenvolvimento):**

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f web
```

3. **Acesse a aplicação:**

- 🌐 **Website:** http://localhost:5000
- **Servidor:** `db`
- **Usuário:** `root`
- **Senha:** `root`
- **Base de dados:** `fooderama`

### 🌍 Acesso Externo com ngrok

Para permitir acesso externo ao servidor (útil para testes ou demonstrações):

1. **Instale o ngrok:** [https://ngrok.com/download](https://ngrok.com/download)

2. **Execute o túnel:**

```bash
# Em um terminal separado, na pasta do projeto
ngrok http 5000
```

3. **Use a URL fornecida pelo ngrok:**

```
https://abc123.ngrok-free.app
```

### ⚡ Comandos Úteis

```bash
# Parar todos os serviços
docker-compose down

# Reiniciar apenas o web server
docker-compose restart web

# Rebuild completo (após mudanças no código)
docker-compose down && docker-compose up -d --build

# Acessar logs de um serviço específico
docker-compose logs -f [web|db|adminer]

# Acessar shell do container
docker-compose exec web bash
docker-compose exec db mysql -u root -proot fooderama
```

## 📋 Funcionalidades

### 🏪 **Sistema de Restaurantes**

- ✅ Cadastro e autenticação de estabelecimentos
- ✅ Perfil do restaurante com horários de funcionamento
- ✅ Gestão completa de pratos (CRUD)
- ✅ Controle automático de estoque
- ✅ Dashboard com pedidos recebidos

### 👤 **Sistema de Clientes**

- ✅ Cadastro e autenticação de usuários
- ✅ Gestão de endereços de entrega
- ✅ Histórico de pedidos
- ✅ Sistema de avaliações
- ✅ Carrinho de compras interativo

### 🍽️ **Gestão de Pratos**

- ✅ CRUD completo com imagens dinâmicas
- ✅ Categorização por tipo de comida
- ✅ Controle de estoque automatizado
- ✅ Status automático (indisponível quando estoque = 0)
- ✅ **Imagens automáticas via Unsplash API**

### 🛒 **Sistema de Pedidos**

- ✅ Carrinho com cálculo de valores
- ✅ Checkout completo
- ✅ Proteção contra condições de corrida
- ✅ Isolamento transacional (READ COMMITTED)
- ✅ Atualizações automáticas de estoque

### 💳 **Pagamentos**

- ✅ Suporte a PIX, débito e crédito
- ✅ Validação de dados de pagamento
- ✅ Integração com endereços de entrega

### 🔒 **Segurança e Performance**

- ✅ **Triggers MySQL** para automação
- ✅ **Isolamento transacional** contra concorrência
- ✅ **Gestão automática de estoque**
- ✅ Sistema de sessões seguro
- ✅ Validação de formulários

---

## 🌐 APIs Integradas

### 🖼️ **Unsplash API - Imagens Dinâmicas**

O sistema utiliza a **Unsplash API** para gerar automaticamente imagens dos pratos baseadas no tipo de comida.

**Configuração:**

1. **Chave de API já configurada:**

```javascript
// app/static/js/food-images.js
const UNSPLASH_ACCESS_KEY = "i7dc1sDWW9VYI4wYRS807fkjL17o77mGaXy3s7y_LWU";
```

2. **Como funciona:**

- Detecta o tipo de prato (pizza, hambúrguer, etc.)
- Busca imagem relacionada no Unsplash
- Aplica cache local para performance
- Fallback automático para imagens padrão

3. **Tipos suportados:**

```javascript
const foodTypeMapping = {
  pizza: "pizza food",
  hamburguer: "burger hamburger",
  lanche: "sandwich snack food",
  massa: "pasta italian food",
  japonesa: "sushi japanese food",
  mexicana: "mexican food tacos",
  churrasco: "barbecue grilled meat",
  doce: "dessert cake sweet",
  sorvete: "ice cream gelato",
  vegetariana: "vegetarian salad healthy",
  "frutos do mar": "seafood fish shrimp",
  arabe: "arabic middle eastern food",
  "comida caseira": "homemade comfort food",
};
```

4. **Uso automático:**

- ✅ Modais de pratos
- ✅ Cards de restaurantes
- ✅ Listagens por tipo
- ✅ Cache inteligente

---

## 🗃️ Estrutura do Banco

O banco de dados é inicializado automaticamente via Docker com os seguintes scripts:

### 📄 Scripts de Inicialização:

1. **`01-fooderama-structure.sql`** - Estrutura completa das tabelas
2. **`02-tipos-prato-data.sql`** - Tipos de comida pré-cadastrados
3. **`03-funcionalidades-fooderama.sql`** - Triggers e automações
4. **`04-isolamento-transacional.sql`** - Configurações de concorrência
5. **`99-teste-inicializacao.sql`** - Dados de teste para desenvolvimento

### 🔗 Principais Tabelas:

```sql
-- Gestão de usuários
cliente, restaurante

-- Catálogo de produtos
prato, tipo_prato

-- Sistema de pedidos
pedido, item_pedido

-- Logística
endereco, endereco_cliente, horafuncionamento

-- Pagamentos
pagamento (PIX, Débito, Crédito)
```

### ⚡ Triggers Automáticos:

- **Gestão de estoque** - Decremento automático ao aceitar pedidos
- **Status de disponibilidade** - Produtos ficam indisponíveis quando estoque = 0
- **Validações de negócio** - Regras automáticas via banco

---

## 🔧 Desenvolvimento

### 📁 Estrutura de Arquivos:

```
fooderama/
├── 🐳 docker-compose.yml        # Orquestração de containers
├── 🐳 Dockerfile               # Imagem da aplicação Python
├── 📋 requirements.txt         # Dependências Python
├── ⚙️ microblog.py             # Entry point da aplicação
├──
├── app/                        # 🏗️ Core da aplicação
│   ├── __init__.py            # Factory pattern do Flask
│   ├── db_config.py           # Configuração MySQL
│   │
│   ├── routes/                # 🛣️ Sistema de rotas modular
│   │   ├── main.py           # Rotas principais (index, tipos)
│   │   ├── auth.py           # Autenticação e registro
│   │   ├── dishes.py         # Gestão de pratos
│   │   ├── orders.py         # Sistema de pedidos
│   │   └── payment.py        # Processamento de pagamentos
│   │
│   ├── templates/            # 🎨 Templates Jinja2
│   │   ├── base.html         # Layout base
│   │   ├── index.html        # Página inicial
│   │   ├── restaurant.html   # Perfil do restaurante
│   │   ├── pratos_por_tipo.html # Listagem por categoria
│   │   └── [outros templates]
│   │
│   └── static/              # 📱 Assets estáticos
│       ├── css/
│       │   ├── output.css   # Tailwind CSS compilado
│       │   └── src/main.css # CSS customizado
│       ├── js/
│       │   ├── food-images.js    # 🖼️ Integração Unsplash
│       │   ├── restaurant.js     # Lógica do restaurante
│       │   └── pratos_por_tipo.js # Listagem de pratos
│       └── images/          # Imagens estáticas
│
└── BANDO DE DADOS/          # 🗄️ Scripts SQL
    ├── 01-fooderama-structure.sql
    ├── 02-tipos-prato-data.sql
    ├── 03-funcionalidades-fooderama.sql
    ├── 04-isolamento-transacional.sql
    └── 99-teste-inicializacao.sql
```

### 🛠️ Stack Tecnológico:

**Backend:**

- 🐍 **Flask 2.3.3** - Framework web Python
- 🔐 **Flask-Login** - Gestão de sessões
- 🌐 **Flask-CORS** - Suporte a requisições cross-origin
- 🗄️ **MySQL Connector** - Driver oficial MySQL

**Frontend:**

- 🎨 **Tailwind CSS** - Framework CSS utilitário
- ⚡ **JavaScript ES6+** - Interatividade moderna
- 🖼️ **Unsplash API** - Imagens dinâmicas
- 📱 **HTML5 Semântico** - Estrutura acessível

**Infraestrutura:**

- 🐳 **Docker + Docker Compose** - Containerização
- 🗄️ **MySQL 8.0** - Banco de dados relacional
- 🌐 **ngrok** - Túneis para acesso externo
- 🔧 **Adminer** - Interface web para MySQL

**DevOps:**

- 🔄 **Hot Reload** - Desenvolvimento ágil
- 📊 **Health Checks** - Monitoramento automático
- 📝 **Logging** - Debug e monitoramento
- 🔒 **Isolamento de Containers** - Segurança

### 🚀 Fluxo de Desenvolvimento:

1. **Modificar código** nos arquivos locais
2. **Hot reload automático** via volumes Docker
3. **Testar localmente** em http://localhost:5000
4. **Debug via logs** com `docker-compose logs -f web`
5. **Acessar banco** via Adminer em http://localhost:8080

### 📱 Responsividade:

- ✅ **Mobile First** - Design otimizado para dispositivos móveis
- ✅ **Breakpoints Tailwind** - sm, md, lg, xl, 2xl
- ✅ **Componentes flexíveis** - Layouts adaptativos
- ✅ **Touch-friendly** - Botões e interações otimizadas

### ✅ Funcionalidades Completas:

- Sistema de autenticação completo
- CRUD de restaurantes e pratos
- Sistema de pedidos com carrinho
- Gestão automática de estoque
- Integração com Unsplash API
- Interface responsiva e moderna
- Proteções contra concorrência

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black?logo=flask)](https://flask.palletsprojects.com)

</div>
