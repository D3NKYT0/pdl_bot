"""
Cog para sistema de votação
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class Vote(commands.Cog):
    """Sistema de votação"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="vote", description="Mostra links para votar no bot")
    async def vote(self, interaction: discord.Interaction):
        """Mostra links de votação"""
        embed = discord.Embed(
            title="🗳️ Vote no Bot PDL",
            description="Ajude o bot a crescer votando em sites de ranking!",
            color=discord.Color.blue()
        )
        
        # Adicionar links de votação (pode ser configurado via env)
        # Por enquanto, deixar genérico
        embed.add_field(
            name="📊 Sites de Ranking",
            value="Links de votação serão adicionados aqui quando disponíveis.\n\n"
                  "Votar ajuda o bot a aparecer em rankings e ganhar mais visibilidade!",
            inline=False
        )
        
        embed.set_footer(text="Obrigado por apoiar o Bot PDL!")
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Vote(bot))

