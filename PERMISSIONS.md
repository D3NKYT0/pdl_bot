# 🔐 Permissões dos Comandos

Este documento lista todas as permissões necessárias para usar cada comando do Bot PDL.

## 📋 Legenda

- **Nenhuma** - Qualquer membro do servidor pode usar
- **Gerenciar Servidor** - Requer permissão "Gerenciar Servidor" (Manage Guild)
- **Login** - Requer login no site via `/login`

---

## 🔧 Configuração [PAINEL]

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/register <domínio>` | **Gerenciar Servidor** | Registra o servidor com um site PDL |
| `/unregister` | **Gerenciar Servidor** | Remove o registro do servidor |
| `/status` | **Gerenciar Servidor** | Verifica o status do registro |

**Permissão Discord:** `manage_guild=True` (Gerenciar Servidor)

---

## 📊 Informações do Servidor [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado (`/register`).

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/online` | **Nenhuma** | Mostra quantos jogadores estão online |
| `/search <nome>` | **Nenhuma** | Busca informações de um personagem |
| `/top-pvp [limite]` | **Nenhuma** | Ranking de PvP |
| `/top-pk [limite]` | **Nenhuma** | Ranking de PK |
| `/top-level [limite]` | **Nenhuma** | Ranking de nível |
| `/top-rich [limite]` | **Nenhuma** | Ranking de riqueza (Adena) |
| `/top-online [limite]` | **Nenhuma** | Ranking de tempo online |

---

## 🐉 Bosses [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado.

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/bosses` | **Nenhuma** | Status dos Grand Bosses |
| `/boss-jewel <ids>` | **Nenhuma** | Localização de Boss Jewels |

---

## 🏆 Olimpíada [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado.

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/olympiad [limite]` | **Nenhuma** | Ranking da Olimpíada |
| `/heroes` | **Nenhuma** | Heróis atuais da Olimpíada |

---

## 🏰 Cercos [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado.

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/siege` | **Nenhuma** | Status dos cercos |
| `/siege-participants <castle_id>` | **Nenhuma** | Participantes de um cerco |

---

## 👥 Clãs e Leilão [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado.

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/clan <nome>` | **Nenhuma** | Informações de um clã |
| `/auction [limite]` | **Nenhuma** | Itens do leilão |
| `/item-search <nome>` | **Nenhuma** | Busca um item |

---

## 🔐 Autenticação [PAINEL]

Todos os comandos desta categoria requerem que o servidor esteja registrado.

| Comando | Permissão | Requisito Adicional |
|---------|-----------|---------------------|
| `/login <username> <password>` | **Nenhuma** | - |
| `/logout` | **Nenhuma** | - |
| `/account` | **Nenhuma** | **Login** (via `/login`) |
| `/dashboard` | **Nenhuma** | **Login** (via `/login`) |
| `/mystats` | **Nenhuma** | **Login** (via `/login`) |

---

## ⚙️ Configurações do Servidor [BOT]

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/config` | **Gerenciar Servidor** | Mostra configurações atuais |
| `/config-set-channel` | **Gerenciar Servidor** | Define canais (feedback, anúncios, logs) |
| `/config-set-notification` | **Gerenciar Servidor** | Ativa/desativa notificações |

**Permissão Discord:** `manage_guild=True` (Gerenciar Servidor)

---

## 🎮 Comandos do Bot [BOT]

| Comando | Permissão | Descrição |
|---------|-----------|-----------|
| `/profile [usuário]` | **Nenhuma** | Perfil de um usuário do Discord |
| `/help [categoria]` | **Nenhuma** | Ajuda sobre o bot |
| `/feedback <mensagem>` | **Nenhuma** | Envia feedback/sugestão |
| `/announce <mensagem>` | **Gerenciar Servidor** | Faz um anúncio no canal configurado |
| `/ping` | **Nenhuma** | Latência do bot |
| `/avatar [usuário]` | **Nenhuma** | Avatar de um usuário |
| `/roll [lados]` | **Nenhuma** | Rola um dado |
| `/choose <opções>` | **Nenhuma** | Escolhe uma opção aleatória |
| `/vote` | **Nenhuma** | Links para votar no bot |

**Permissão Discord para `/announce`:** `manage_guild=True` (Gerenciar Servidor)

---

## 📝 Resumo de Permissões

### Comandos que requerem "Gerenciar Servidor"
- `/register` - Registrar servidor
- `/unregister` - Remover registro
- `/status` - Verificar status do registro
- `/config` - Ver configurações
- `/config-set-channel` - Configurar canais
- `/config-set-notification` - Configurar notificações
- `/announce` - Fazer anúncios

### Comandos que requerem Login no Site
- `/account`
- `/dashboard`
- `/mystats`

### Comandos sem restrição de permissão
- Todos os outros comandos podem ser usados por qualquer membro do servidor

---

## 🔒 Permissões do Bot no Servidor

O bot precisa das seguintes permissões no servidor Discord para funcionar corretamente:

### Permissões Básicas (Obrigatórias)
- ✅ **Ver Canais** (View Channels)
- ✅ **Enviar Mensagens** (Send Messages)
- ✅ **Incorporar Links** (Embed Links)
- ✅ **Ler Histórico de Mensagens** (Read Message History)
- ✅ **Usar Comandos de Aplicativo** (Use Application Commands)

### Permissões Adicionais (Recomendadas)
- ✅ **Gerenciar Mensagens** (Manage Messages) - Para anúncios
- ✅ **Anexar Arquivos** (Attach Files) - Para alguns recursos

### Permissões por Canal

Para comandos que enviam mensagens em canais específicos, o bot precisa das seguintes permissões **no canal**:

**Canal de Anúncios:**
- Ver Canais
- Enviar Mensagens
- Incorporar Links

**Canal de Feedback:**
- Ver Canais
- Enviar Mensagens
- Incorporar Links

**Canal de Logs:**
- Ver Canais
- Enviar Mensagens
- Incorporar Links

---

## ⚠️ Notas Importantes

1. **Comandos [PAINEL]**: Requerem que o servidor esteja registrado via `/register`
2. **Comandos [BOT]**: Funcionam independentemente do registro
3. **Permissões do Discord**: As permissões são verificadas automaticamente pelo Discord
4. **Permissões do Bot**: O bot precisa ter permissões adequadas nos canais onde envia mensagens

---

**Última atualização:** 2025-12-13
