# Bot Discord PDL

Bot global para integração com instâncias do Painel Definitivo Lineage (PDL). O bot pode se conectar a qualquer instância do site via API REST.

## 🚀 Características

- **Bot Global**: Um único bot pode servir múltiplos servidores Discord
- **Multi-instância**: Conecta-se a diferentes instâncias do site PDL
- **MongoDB**: Usa MongoDB para gerenciar dados do bot
- **Slash Commands**: Interface moderna com comandos slash do Discord
- **API Integration**: Integração completa com a API REST do PDL

## 📋 Pré-requisitos

- Docker e Docker Compose (recomendado)
- OU Python 3.10+ e MongoDB (local ou remoto)
- Token do Bot Discord
- Acesso a instâncias do site PDL com API habilitada

## 🔧 Instalação

### Opção 1: Docker (Recomendado)

1. Configure as variáveis de ambiente:
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

2. Configure o arquivo `.env`:
```env
DISCORD_BOT_TOKEN=seu_token_do_discord
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=pdl_bot
```

**Nota:** Quando usando Docker, use `mongodb://mongodb:27017` (nome do serviço) ao invés de `localhost`.

3. Construa e inicie os containers:
```bash
docker-compose up -d
```

4. Verifique os logs:
```bash
docker-compose logs -f bot
```

5. Para parar:
```bash
docker-compose down
```

### Opção 2: Instalação Local

1. Clone o repositório ou copie os arquivos do bot

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

4. Configure o arquivo `.env`:
```env
DISCORD_BOT_TOKEN=seu_token_do_discord
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pdl_bot
```

## 🎮 Como Usar

### 1. Registrar um Servidor

No servidor Discord, use o comando:
```
/register l2iron.com
```

Isso vincula o servidor Discord ao site `l2iron.com`.

### 2. Comandos Disponíveis

#### Configuração
- `/register <domínio>` - Registra o servidor com um site PDL
- `/unregister` - Remove o registro do servidor
- `/status` - Verifica o status do registro

#### Informações do Servidor
- `/online` - Mostra jogadores online
- `/top-pvp [limite]` - Ranking de PvP
- `/top-pk [limite]` - Ranking de PK
- `/top-level [limite]` - Ranking de nível
- `/top-rich [limite]` - Ranking de riqueza (Adena)
- `/top-online [limite]` - Ranking de tempo online
- `/search <nome>` - Busca um personagem

#### Bosses
- `/bosses` - Status dos Grand Bosses
- `/boss-jewel <ids>` - Localização de Boss Jewels (ex: 6656,6657)

#### Olimpíada
- `/olympiad [limite]` - Ranking da Olimpíada
- `/heroes` - Heróis atuais da Olimpíada

#### Cercos
- `/siege` - Status dos cercos
- `/siege-participants <castle_id>` - Participantes de um cerco

#### Clãs e Leilão
- `/clan <nome>` - Informações de um clã
- `/auction [limite]` - Itens do leilão
- `/item-search <nome>` - Busca um item

#### Comandos Autenticados [PAINEL] (Requerem Login)
- `/login <username> <password>` - Faz login no site
- `/logout` - Faz logout
- `/panel-profile` - Mostra seu perfil no site
- `/panel-dashboard` - Mostra seu dashboard
- `/panel-stats` - Mostra suas estatísticas

#### Comandos do Bot [BOT]
- `/profile [usuário]` - Mostra perfil de um usuário do Discord

#### Ajuda
- `/help` - Mostra informações sobre o bot

## 🏗️ Estrutura do Projeto

```
bot/
├── main.py                 # Arquivo principal do bot
├── bot/
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py          # Configurações
│   │   ├── database.py        # Gerenciamento MongoDB
│   │   ├── site_client.py      # Cliente para API do site
│   │   ├── rate_limiter.py    # Sistema de rate limiting
│   │   └── auth_manager.py    # Gerenciamento de autenticação
│   └── cogs/
│       ├── server_detection.py  # Detecção e registro
│       ├── server_info.py       # Informações do servidor
│       ├── player_commands.py   # Comandos para jogadores
│       └── help.py              # Ajuda
├── requirements.txt
├── .env.example
└── README.md
```

## 🔌 Integração com o Site

O bot se conecta à API REST do site PDL através dos seguintes endpoints:

- `GET /api/v1/server/status/` - Status do servidor
- `GET /api/v1/server/players-online/` - Jogadores online
- `GET /api/v1/server/top-pvp/` - Ranking PvP
- `GET /api/v1/server/top-pk/` - Ranking PK
- `GET /api/v1/server/top-level/` - Ranking nível
- `GET /api/v1/search/character/` - Busca de personagem
- `GET /api/v1/health/` - Health check

## 📊 Banco de Dados

O bot usa MongoDB para armazenar:

- **servers**: Registro de servidores Discord vinculados a domínios
  - `discord_guild_id`: ID do servidor Discord
  - `site_domain`: Domínio do site PDL
  - `server_name`: Nome do servidor
  - `is_active`: Status ativo/inativo
  - `created_at`: Data de criação

## 🚀 Executar

### Com Docker
```bash
docker-compose up -d
```

### Localmente
```bash
python main.py
```

## 📝 Logs

### Com Docker
Os logs são salvos em `./logs/` e também podem ser visualizados com:
```bash
docker-compose logs -f bot
```

### Localmente
Os logs são salvos em `bot.log` e também exibidos no console.

## 🔒 Segurança

- O bot não armazena tokens ou senhas
- Todas as comunicações com a API são via HTTPS
- MongoDB deve estar protegido com autenticação em produção

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto no `.env`
- Verifique se o bot tem as permissões necessárias no servidor

### Erro ao conectar à API
- Verifique se o domínio está correto
- Verifique se a API do site está acessível
- Verifique se o site tem CORS configurado corretamente

### Erro ao conectar ao MongoDB
- Verifique se o MongoDB está rodando
- Verifique a URI de conexão no `.env`

## 📄 Licença

Este bot é parte do projeto PDL e segue a mesma licença.
