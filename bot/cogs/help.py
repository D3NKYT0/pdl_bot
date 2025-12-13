"""
Cog de ajuda melhorado
"""

import discord
from discord import app_commands
from discord.ext import commands


class HelpCommand(commands.Cog):
    """Comando de ajuda melhorado"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="[BOT] Mostra informações sobre o bot e seus comandos")
    @app_commands.describe(category="Categoria de comandos para ver detalhes")
    @app_commands.choices(category=[
        app_commands.Choice(name="Todas as Categorias", value="all"),
        app_commands.Choice(name="Configuração", value="config"),
        app_commands.Choice(name="Informações do Servidor", value="server"),
        app_commands.Choice(name="Bosses", value="bosses"),
        app_commands.Choice(name="Olimpíada", value="olympiad"),
        app_commands.Choice(name="Cercos", value="siege"),
        app_commands.Choice(name="Clãs e Leilão", value="clan"),
        app_commands.Choice(name="Rankings", value="rankings"),
        app_commands.Choice(name="Autenticação", value="auth"),
        app_commands.Choice(name="Feedback", value="feedback"),
        app_commands.Choice(name="Configurações do Servidor", value="server_config"),
    ])
    async def help(self, interaction: discord.Interaction, 
                   category: app_commands.Choice[str] = None):
        """Mostra ajuda categorizada"""
        
        if not category or category.value == "all":
            # Mostrar visão geral
            embed = discord.Embed(
                title="🤖 Bot PDL - Ajuda",
                description="Bot para integração com servidores Lineage 2 PDL\n\n"
                          "Use `/help <categoria>` para ver comandos específicos de cada categoria.",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Configuração",
                value="`/register` - Registra servidor\n"
                      "`/unregister` - Remove registro\n"
                      "`/status` - Status do registro",
                inline=True
            )
            
            embed.add_field(
                name="📊 Servidor",
                value="`/online` - Jogadores online\n"
                      "`/search` - Buscar personagem\n"
                      "`/top-pvp`, `/top-pk`, `/top-level` - Rankings",
                inline=True
            )
            
            embed.add_field(
                name="🐉 Bosses",
                value="`/bosses` - Status dos bosses\n"
                      "`/boss-jewel` - Localização de jewels",
                inline=True
            )
            
            embed.add_field(
                name="🏆 Olimpíada",
                value="`/olympiad` - Ranking\n"
                      "`/heroes` - Heróis atuais",
                inline=True
            )
            
            embed.add_field(
                name="🏰 Cercos",
                value="`/siege` - Status dos cercos\n"
                      "`/siege-participants` - Participantes",
                inline=True
            )
            
            embed.add_field(
                name="👥 Clãs e Leilão",
                value="`/clan` - Info do clã\n"
                      "`/auction` - Itens do leilão\n"
                      "`/item-search` - Buscar item",
                inline=True
            )
            
            embed.add_field(
                name="💰 Rankings Adicionais",
                value="`/top-rich` - Mais ricos\n"
                      "`/top-online` - Mais tempo online",
                inline=True
            )
            
            embed.add_field(
                name="🔐 Autenticação [PAINEL]",
                value="`/login` - Fazer login\n"
                      "`/logout` - Fazer logout\n"
                      "`/account`, `/dashboard`, `/mystats` - Dados pessoais",
                inline=True
            )
            
            embed.add_field(
                name="💬 Outros",
                value="`/feedback` - Enviar feedback\n"
                      "`/config` - Configurar servidor",
                inline=True
            )
            
            embed.set_footer(text="Bot PDL v2.0.0 | Use /help <categoria> para mais detalhes")
            
        else:
            # Mostrar categoria específica
            embed = self._get_category_help(category.value)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _get_category_help(self, category: str) -> discord.Embed:
        """Retorna embed de ajuda para uma categoria específica"""
        
        if category == "config":
            embed = discord.Embed(
                title="📝 Configuração",
                description="Comandos para configurar o bot no servidor",
                color=discord.Color.green()
            )
            embed.add_field(
                name="`/register <domínio>`",
                value="Registra este servidor Discord com um site PDL.\n"
                      "Exemplo: `/register l2iron.com`",
                inline=False
            )
            embed.add_field(
                name="`/unregister`",
                value="Remove o registro do servidor. O bot não funcionará mais aqui.",
                inline=False
            )
            embed.add_field(
                name="`/status`",
                value="Verifica o status do registro e mostra qual site está vinculado.",
                inline=False
            )
        
        elif category == "server":
            embed = discord.Embed(
                title="📊 Informações do Servidor",
                description="Comandos para obter informações do servidor de jogo",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="`/online`",
                value="Mostra quantos jogadores estão online no momento.",
                inline=False
            )
            embed.add_field(
                name="`/search <nome>`",
                value="Busca informações sobre um personagem.\n"
                      "Exemplo: `/search PlayerName`",
                inline=False
            )
            embed.add_field(
                name="`/top-pvp [limite]`",
                value="Mostra ranking de PvP (padrão: 10, máximo: 20).",
                inline=False
            )
            embed.add_field(
                name="`/top-pk [limite]`",
                value="Mostra ranking de PK (padrão: 10, máximo: 20).",
                inline=False
            )
            embed.add_field(
                name="`/top-level [limite]`",
                value="Mostra ranking de nível (padrão: 10, máximo: 20).",
                inline=False
            )
        
        elif category == "bosses":
            embed = discord.Embed(
                title="🐉 Bosses",
                description="Comandos relacionados a Grand Bosses",
                color=discord.Color.red()
            )
            embed.add_field(
                name="`/bosses`",
                value="Mostra status de todos os Grand Bosses (vivo/morto e tempo de respawn).",
                inline=False
            )
            embed.add_field(
                name="`/boss-jewel <ids>`",
                value="Busca localização de Boss Jewels.\n"
                      "Exemplo: `/boss-jewel 6656,6657`",
                inline=False
            )
        
        elif category == "olympiad":
            embed = discord.Embed(
                title="🏆 Olimpíada",
                description="Comandos relacionados à Olimpíada",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="`/olympiad [limite]`",
                value="Mostra ranking da Olimpíada (padrão: 10, máximo: 20).",
                inline=False
            )
            embed.add_field(
                name="`/heroes`",
                value="Mostra os heróis atuais da Olimpíada.",
                inline=False
            )
        
        elif category == "siege":
            embed = discord.Embed(
                title="🏰 Cercos",
                description="Comandos relacionados aos cercos de castelos",
                color=discord.Color.purple()
            )
            embed.add_field(
                name="`/siege`",
                value="Mostra status de todos os castelos e seus cercos.",
                inline=False
            )
            embed.add_field(
                name="`/siege-participants <castle_id>`",
                value="Mostra participantes de um cerco específico.\n"
                      "Castle ID: 1-9",
                inline=False
            )
        
        elif category == "clan":
            embed = discord.Embed(
                title="👥 Clãs e Leilão",
                description="Comandos relacionados a clãs e leilão",
                color=discord.Color.green()
            )
            embed.add_field(
                name="`/clan <nome>`",
                value="Busca informações sobre um clã (líder, nível, membros, etc.).",
                inline=False
            )
            embed.add_field(
                name="`/auction [limite]`",
                value="Mostra itens disponíveis no leilão (padrão: 10, máximo: 20).",
                inline=False
            )
            embed.add_field(
                name="`/item-search <nome>`",
                value="Busca um item no banco de dados do jogo.",
                inline=False
            )
        
        elif category == "rankings":
            embed = discord.Embed(
                title="💰 Rankings Adicionais",
                description="Rankings especiais",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="`/top-rich [limite]`",
                value="Mostra ranking de riqueza (Adena).",
                inline=False
            )
            embed.add_field(
                name="`/top-online [limite]`",
                value="Mostra ranking de tempo online.",
                inline=False
            )
        
        elif category == "auth":
            embed = discord.Embed(
                title="🔐 Autenticação",
                description="Comandos que requerem login no site",
                color=discord.Color.dark_blue()
            )
            embed.add_field(
                name="`/login <username> <password>`",
                value="Faz login no site PDL. Suas credenciais são armazenadas de forma segura.\n"
                      "⚠️ Use apenas em canais privados!",
                inline=False
            )
            embed.add_field(
                name="`/logout`",
                value="Faz logout e remove suas credenciais.",
                inline=False
            )
            embed.add_field(
                name="`/account`",
                value="[PAINEL] Mostra seu perfil no site (requer login).",
                inline=False
            )
            embed.add_field(
                name="`/dashboard`",
                value="[PAINEL] Mostra seu dashboard com estatísticas (requer login).",
                inline=False
            )
            embed.add_field(
                name="`/mystats`",
                value="[PAINEL] Mostra suas estatísticas detalhadas (requer login).",
                inline=False
            )
            embed.add_field(
                name="`/profile`",
                value="[BOT] Mostra perfil de um usuário do Discord (não requer login).",
                inline=False
            )
        
        elif category == "feedback":
            embed = discord.Embed(
                title="💬 Feedback",
                description="Sistema de feedback e sugestões",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="`/feedback <mensagem>`",
                value="Envia feedback, sugestão ou reporta um bug.\n"
                      "Seu feedback será enviado para os desenvolvedores.",
                inline=False
            )
        
        elif category == "server_config":
            embed = discord.Embed(
                title="⚙️ Configurações do Servidor",
                description="Configurações administrativas (requer permissão 'Gerenciar Servidor')",
                color=discord.Color.dark_grey()
            )
            embed.add_field(
                name="`/config`",
                value="Mostra as configurações atuais do servidor.",
                inline=False
            )
            embed.add_field(
                name="`/config-set-channel`",
                value="Define um canal de configuração.\n\n"
                      "**Tipos de canal:**\n"
                      "- Canal de Feedback\n"
                      "- Canal de Anúncios\n"
                      "- Canal de Logs\n\n"
                      "Deixe o canal vazio para remover a configuração.",
                inline=False
            )
            embed.add_field(
                name="`/config-set-notification`",
                value="Ativa ou desativa notificações.\n\n"
                      "**Tipos de notificação:**\n"
                      "- Notificações de Bosses\n"
                      "- Notificações de Cercos\n"
                      "- Notificações de Olimpíada\n"
                      "- Notificações de Entrada de Membros\n"
                      "- Notificações de Saída de Membros",
                inline=False
            )
        
        else:
            embed = discord.Embed(
                title="❌ Categoria não encontrada",
                description="Use `/help` para ver todas as categorias disponíveis.",
                color=discord.Color.red()
            )
        
        embed.set_footer(text="Bot PDL v2.0.0")
        return embed


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
