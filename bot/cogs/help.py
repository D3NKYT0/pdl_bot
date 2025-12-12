"""
Cog de ajuda
"""

import discord
from discord import app_commands
from discord.ext import commands


class HelpCommand(commands.Cog):
    """Comando de ajuda"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Mostra informações sobre o bot")
    async def help(self, interaction: discord.Interaction):
        """Mostra ajuda"""
        embed = discord.Embed(
            title="🤖 Bot PDL - Ajuda",
            description="Bot para integração com servidores Lineage 2 PDL",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📝 Configuração",
            value="`/register <domínio>` - Registra este servidor com um site PDL\n"
                  "`/unregister` - Remove o registro do servidor\n"
                  "`/status` - Verifica o status do registro",
            inline=False
        )
        
        embed.add_field(
            name="📊 Informações do Servidor",
            value="`/online` - Jogadores online\n"
                  "`/top-pvp` - Ranking de PvP\n"
                  "`/top-pk` - Ranking de PK\n"
                  "`/top-level` - Ranking de nível\n"
                  "`/search <nome>` - Busca um personagem",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Sobre",
            value="Este bot se conecta à API do site PDL para exibir informações do servidor de jogo.",
            inline=False
        )
        
        embed.set_footer(text="Bot PDL v1.0.0")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
