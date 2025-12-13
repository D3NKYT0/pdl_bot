# 🤖 Bot Discord PDL

Bot global para integração com instâncias do **Painel Definitivo Lineage (PDL)**. Um único bot pode servir múltiplos servidores Discord, conectando-se a diferentes instâncias do site via API REST.

## 📖 Sobre o Projeto

O **Bot PDL** é uma solução completa para integração entre servidores Discord e servidores Lineage 2 que utilizam o sistema PDL. Ele permite que administradores e jogadores acessem informações do jogo diretamente pelo Discord, facilitando a comunicação e o acesso a dados importantes do servidor.

### ✨ Principais Funcionalidades

- 🌐 **Bot Global**: Um único bot serve múltiplos servidores Discord simultaneamente
- 🔌 **Multi-instância**: Conecta-se a diferentes instâncias do site PDL via API REST
- 📊 **Informações em Tempo Real**: Acessa dados do servidor, rankings, bosses, cercos e muito mais
- 🔐 **Sistema de Autenticação**: Login integrado para acessar informações pessoais do site
- ⚙️ **Configurável**: Sistema completo de configurações por servidor
- 📢 **Anúncios e Notificações**: Sistema de anúncios e notificações automáticas
- 💬 **Feedback**: Sistema integrado para receber feedback dos usuários
- 🎮 **Comandos Utilitários**: Ferramentas úteis como dados, escolhas aleatórias, etc.

## 🚀 Características Técnicas

- **Framework**: Discord.py 2.3.2+
- **Banco de Dados**: MongoDB (Motor async driver)
- **API**: Integração completa com API REST do PDL
- **Comandos**: Interface moderna com Slash Commands
- **Rate Limiting**: Sistema de controle de taxa de requisições
- **Docker**: Suporte completo para containerização

## 📋 Pré-requisitos

- **Docker e Docker Compose** (recomendado)
- **OU** Python 3.10+ e MongoDB (local ou remoto)
- **Token do Bot Discord** (obtido em [Discord Developer Portal](https://discord.com/developers/applications))
- **Acesso a instâncias do site PDL** com API habilitada
- **Intenções do Bot** habilitadas no Discord Developer Portal:
  - ✅ Server Members Intent
  - ✅ Message Content Intent
  - ✅ Presence Intent (para ver status dos usuários)

## 🔧 Instalação

### Opção 1: Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd BOT
```

2. **Configure as variáveis de ambiente:**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Configure o arquivo `.env`:**
```env
DISCORD_BOT_TOKEN=seu_token_do_discord
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DB=pdl_bot
LOG_FILE=bot.log
```

**Nota:** Quando usando Docker, use `mongodb://mongodb:27017` (nome do serviço) ao invés de `localhost`.

4. **Construa e inicie os containers:**
```bash
docker-compose build
docker-compose up -d
```

5. **Verifique os logs:**
```bash
docker-compose logs -f bot
```

6. **Para parar:**
```bash
docker-compose down
```

### Opção 2: Instalação Local

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd BOT
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

4. **Configure o arquivo `.env`:**
```env
DISCORD_BOT_TOKEN=seu_token_do_discord
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=pdl_bot
LOG_FILE=bot.log
```

5. **Execute o bot:**
```bash
python main.py
```

## 🎮 Como Usar

### 1. Registrar um Servidor

Antes de usar os comandos do painel, você precisa registrar seu servidor Discord com um site PDL:

```
/register pdl.denky.dev.br
```

Isso vincula o servidor Discord ao site `https://pdl.denky.dev.br/`. Após o registro, todos os comandos `[PAINEL]` estarão disponíveis.

### 2. Configurar o Bot

Configure canais e notificações usando os comandos de configuração:

```
/config - Ver configurações atuais
/config-set-channel - Configurar canais (feedback, anúncios, logs)
/config-set-notification - Ativar/desativar notificações
```

### 3. Permissões dos Comandos

📋 **Para ver a lista completa de permissões de cada comando, consulte [PERMISSIONS.md](PERMISSIONS.md)**

**Resumo rápido:**
- **Maioria dos comandos**: Qualquer membro pode usar
- **Comandos administrativos**: Requerem permissão "Gerenciar Servidor"
  - `/register`, `/unregister`, `/status` - Configuração do servidor
  - `/config`, `/config-set-channel`, `/config-set-notification` - Configurações do bot
  - `/announce` - Fazer anúncios
- **Comandos autenticados**: Requerem login no site via `/login`
  - `/account`, `/dashboard`, `/mystats`

## 📚 Comandos Disponíveis

### 🔧 Configuração [PAINEL]

Comandos para configurar e gerenciar o registro do servidor.

| Comando | Descrição |
|---------|-----------|
| `/register <domínio>` | Registra o servidor com um site PDL |
| `/unregister` | Remove o registro do servidor |
| `/status` | Verifica o status do registro e conectividade da API |

### 📊 Informações do Servidor [PAINEL]

Comandos para obter informações gerais do servidor.

| Comando | Descrição |
|---------|-----------|
| `/online` | Mostra quantos jogadores estão online no momento |
| `/search <nome>` | Busca informações de um personagem |
| `/top-pvp [limite]` | Ranking de PvP (padrão: 10, máximo: 20) |
| `/top-pk [limite]` | Ranking de PK (padrão: 10, máximo: 20) |
| `/top-level [limite]` | Ranking de nível (padrão: 10, máximo: 20) |
| `/top-rich [limite]` | Ranking de riqueza em Adena (padrão: 10, máximo: 20) |
| `/top-online [limite]` | Ranking de tempo online (padrão: 10, máximo: 20) |

### 🐉 Bosses [PAINEL]

Comandos relacionados aos Grand Bosses do servidor.

| Comando | Descrição |
|---------|-----------|
| `/bosses` | Mostra status de todos os Grand Bosses (vivo/morto e tempo de respawn) |
| `/boss-jewel <ids>` | Busca localização de Boss Jewels (ex: `6656,6657`) |

### 🏆 Olimpíada [PAINEL]

Comandos relacionados ao sistema de Olimpíada.

| Comando | Descrição |
|---------|-----------|
| `/olympiad [limite]` | Mostra ranking da Olimpíada (padrão: 10) |
| `/heroes` | Mostra os heróis atuais da Olimpíada |

### 🏰 Cercos [PAINEL]

Comandos relacionados aos cercos de castelos.

| Comando | Descrição |
|---------|-----------|
| `/siege` | Mostra status de todos os castelos e seus cercos |
| `/siege-participants <castle_id>` | Mostra participantes de um cerco específico |

### 👥 Clãs e Leilão [PAINEL]

Comandos para informações de clãs e leilão.

| Comando | Descrição |
|---------|-----------|
| `/clan <nome>` | Busca informações de um clã |
| `/auction [limite]` | Mostra itens disponíveis no leilão (padrão: 10) |
| `/item-search <nome>` | Busca um item no banco de dados |

### 🔐 Autenticação [PAINEL]

Comandos que requerem login no site para acessar informações pessoais.

| Comando | Descrição |
|---------|-----------|
| `/login <username> <password>` | Faz login no site (requer autenticação) |
| `/logout` | Faz logout do site |
| `/account` | Mostra seu perfil no site (requer login) |
| `/dashboard` | Mostra seu dashboard pessoal (requer login) |
| `/mystats` | Mostra suas estatísticas pessoais (requer login) |

### ⚙️ Configurações do Servidor [BOT]

Comandos administrativos para configurar o bot no servidor.

| Comando | Descrição | Permissão |
|---------|-----------|-----------|
| `/config` | Mostra as configurações atuais do servidor | Gerenciar Servidor |
| `/config-set-channel` | Define canais (feedback, anúncios, logs) | Gerenciar Servidor |
| `/config-set-notification` | Ativa/desativa notificações automáticas | Gerenciar Servidor |

**Tipos de Canal:**
- **Canal de Feedback**: Recebe feedbacks enviados pelos usuários
- **Canal de Anúncios**: Canal onde anúncios são enviados
- **Canal de Logs**: Canal para logs e auditoria do servidor

**Tipos de Notificação:**
- Notificações de Bosses
- Notificações de Cercos
- Notificações de Olimpíada
- Notificações de Entrada de Membros
- Notificações de Saída de Membros

### 🎮 Comandos do Bot [BOT]

Comandos gerais do bot que não dependem do registro do servidor.

| Comando | Descrição |
|---------|-----------|
| `/profile [usuário]` | Mostra perfil de um usuário do Discord |
| `/help [categoria]` | Mostra informações sobre o bot e seus comandos |
| `/feedback <mensagem>` | Envia feedback, sugestão ou reporta um bug |
| `/announce <mensagem>` | Faz um anúncio no canal configurado (requer permissão) |
| `/ping` | Mostra a latência do bot |
| `/avatar [usuário]` | Mostra o avatar de um usuário |
| `/roll [lados]` | Rola um dado (padrão: 6 lados) |
| `/choose <opções>` | Escolhe uma opção aleatória (separadas por vírgula) |
| `/vote` | Mostra links para votar no bot |

## 🏗️ Estrutura do Projeto

```
BOT/
├── main.py                      # Arquivo principal do bot
├── bot/
│   ├── __init__.py
│   ├── core/                    # Módulos principais
│   │   ├── config.py           # Configurações e variáveis de ambiente
│   │   ├── database.py         # Gerenciamento MongoDB
│   │   ├── site_client.py      # Cliente HTTP para API do site
│   │   ├── rate_limiter.py    # Sistema de rate limiting
│   │   └── auth_manager.py    # Gerenciamento de autenticação JWT
│   └── cogs/                   # Extensões do bot (comandos)
│       ├── server_detection.py # Detecção e registro de servidores
│       ├── server_info.py      # Informações do servidor (online, rankings)
│       ├── player_commands.py # Comandos de jogadores (bosses, olimpíada, etc.)
│       ├── server_config.py    # Configurações do servidor
│       ├── user_profile.py     # Perfil de usuários
│       ├── help.py             # Sistema de ajuda
│       ├── feedback.py         # Sistema de feedback
│       ├── announcements.py   # Sistema de anúncios
│       ├── notifications.py    # Notificações automáticas
│       ├── logging_system.py   # Sistema de logs e auditoria
│       ├── utility.py          # Comandos utilitários
│       └── vote.py             # Sistema de votação
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Imagem Docker
├── docker-compose.yml          # Configuração Docker Compose
├── env.example                 # Exemplo de variáveis de ambiente
└── README.md                   # Este arquivo
```

## 🔌 Integração com a API

O bot se conecta à API REST do site PDL através dos seguintes endpoints:

### Endpoints Públicos
- `GET /api/v1/health/` - Health check
- `GET /api/v1/server/status/` - Status do servidor
- `GET /api/v1/server/players-online/` - Jogadores online
- `GET /api/v1/server/top-pvp/` - Ranking PvP
- `GET /api/v1/server/top-pk/` - Ranking PK
- `GET /api/v1/server/top-level/` - Ranking de nível
- `GET /api/v1/server/top-rich/` - Ranking de riqueza
- `GET /api/v1/server/top-online/` - Ranking de tempo online
- `GET /api/v1/server/grandboss-status/` - Status dos Grand Bosses
- `GET /api/v1/server/olympiad/` - Ranking da Olimpíada
- `GET /api/v1/server/siege-status/` - Status dos cercos
- `GET /api/v1/search/character/` - Busca de personagem
- `GET /api/v1/search/clan/` - Busca de clã
- `GET /api/v1/search/item/` - Busca de item
- `GET /api/v1/auction/` - Itens do leilão

### Endpoints Autenticados
- `POST /api/v1/auth/login/` - Login (retorna JWT)
- `GET /api/v1/user/profile/` - Perfil do usuário
- `GET /api/v1/user/dashboard/` - Dashboard do usuário
- `GET /api/v1/user/stats/` - Estatísticas do usuário

## 📊 Banco de Dados

O bot usa MongoDB para armazenar:

### Coleção: `servers`
Registro de servidores Discord vinculados a domínios PDL
```json
{
  "discord_guild_id": "123456789",
  "site_domain": "pdl.denky.dev.br",
  "server_name": "Iron L2",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Coleção: `server_configs`
Configurações por servidor Discord
```json
{
  "guild_id": "123456789",
  "feedback_channel_id": "987654321",
  "announcement_channel_id": "987654322",
  "log_channel_id": "987654323",
  "boss_notifications": true,
  "siege_notifications": true,
  "olympiad_notifications": false,
  "member_join_notifications": true,
  "member_leave_notifications": true
}
```

### Coleção: `feedback`
Feedbacks enviados pelos usuários
```json
{
  "user_id": "123456789",
  "guild_id": "987654321",
  "message": "Ótimo bot!",
  "server_name": "Iron L2",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Coleção: `auth_tokens`
Tokens de autenticação JWT (criptografados)
```json
{
  "user_id": "123456789",
  "token": "encrypted_jwt_token",
  "expires_at": "2024-01-02T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🚀 Executar

### Com Docker
```bash
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f bot

# Parar
docker-compose down

# Rebuild completo
docker-compose build --no-cache
docker-compose up -d
```

### Localmente
```bash
# Executar o bot
python main.py

# Ou com Python 3 explicitamente
python3 main.py
```

## 📝 Logs

### Com Docker
Os logs são salvos em `./logs/` e também podem ser visualizados com:
```bash
docker-compose logs -f bot
```

### Localmente
Os logs são salvos em `bot.log` (ou o arquivo especificado em `LOG_FILE`) e também exibidos no console.

## 🔒 Segurança

- ✅ O bot **não armazena senhas** em texto plano
- ✅ Tokens JWT são **criptografados** antes de serem salvos
- ✅ Todas as comunicações com a API são via **HTTPS**
- ✅ Sistema de **rate limiting** para prevenir abuso
- ✅ MongoDB deve estar protegido com **autenticação** em produção
- ✅ Tokens do Discord devem ser mantidos **seguros** e nunca commitados

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `DISCORD_BOT_TOKEN` | Token do bot Discord | ✅ Sim |
| `MONGODB_URI` | URI de conexão do MongoDB | ✅ Sim |
| `MONGODB_DB` | Nome do banco de dados | ✅ Sim |
| `LOG_FILE` | Arquivo de log (padrão: `bot.log`) | ❌ Não |

### Permissões do Bot

O bot precisa das seguintes permissões no servidor Discord:

**Permissões Básicas (Obrigatórias):**
- ✅ **Ver Canais** (View Channels)
- ✅ **Enviar Mensagens** (Send Messages)
- ✅ **Incorporar Links** (Embed Links)
- ✅ **Ler Histórico de Mensagens** (Read Message History)
- ✅ **Usar Comandos de Aplicativo** (Use Application Commands)

**Permissões Adicionais (Recomendadas):**
- ✅ **Gerenciar Mensagens** (Manage Messages) - Para anúncios
- ✅ **Anexar Arquivos** (Attach Files) - Para alguns recursos

**Permissões por Canal:**
Para canais configurados (anúncios, feedback, logs), o bot precisa de:
- Ver Canais
- Enviar Mensagens
- Incorporar Links

📋 **Para detalhes completos sobre permissões de comandos, veja [PERMISSIONS.md](PERMISSIONS.md)**

### Intenções do Bot (Discord Developer Portal)

**⚠️ IMPORTANTE:** As intenções devem ser habilitadas no [Discord Developer Portal](https://discord.com/developers/applications):

1. Acesse https://discord.com/developers/applications
2. Selecione seu bot
3. Vá em **"Bot"** → **"Privileged Gateway Intents"**
4. Habilite as seguintes intenções:

- ✅ **SERVER MEMBERS INTENT** - Para ver membros do servidor
- ✅ **MESSAGE CONTENT INTENT** - Para ler conteúdo de mensagens  
- ✅ **PRESENCE INTENT** - Para ver status dos usuários (online/offline/ausente/ocupado)

**Nota:** Após habilitar as intenções, você **DEVE reiniciar o bot** para que as mudanças tenham efeito. Sem a intenção PRESENCE INTENT habilitada, o comando `/profile` sempre mostrará status como "offline", mesmo que o usuário esteja online.

## 🐛 Troubleshooting

### Bot não responde
- ✅ Verifique se o token está correto no `.env`
- ✅ Verifique se o bot está online no Discord Developer Portal
- ✅ Verifique se o bot tem as permissões necessárias no servidor
- ✅ Verifique os logs para erros: `docker-compose logs -f bot`

### Erro ao conectar à API
- ✅ Verifique se o domínio está correto no comando `/register`
- ✅ Verifique se a API do site está acessível
- ✅ Verifique se o site tem CORS configurado corretamente
- ✅ Use `/status` para verificar a conectividade

### Erro ao conectar ao MongoDB
- ✅ Verifique se o MongoDB está rodando
- ✅ Verifique a URI de conexão no `.env`
- ✅ Com Docker, use `mongodb://mongodb:27017` (nome do serviço)
- ✅ Localmente, use `mongodb://localhost:27017`

### Comandos não aparecem
- ✅ Aguarde alguns minutos após iniciar o bot (sincronização de comandos)
- ✅ Verifique se o bot tem permissão "Usar Comandos de Aplicativo"
- ✅ Tente reiniciar o bot: `docker-compose restart bot`

### Status do usuário mostra "offline"
- ✅ Habilite "PRESENCE INTENT" no Discord Developer Portal
- ✅ Reinicie o bot após habilitar a intenção

## 📄 Licença

Este bot é parte do projeto PDL e segue a mesma licença.

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte, use o comando `/feedback` no Discord ou abra uma issue no repositório.

---

**Desenvolvido com ❤️ para a comunidade Lineage 2 PDL**
