"""
Cog para comandos utilitários diversos
"""

import logging
import random
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class Utility(commands.Cog):
    """Comandos utilitários"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="avatar", description="[BOT] Mostra o avatar de um usuário")
    @app_commands.describe(user="Usuário para ver o avatar (deixe vazio para ver o seu)")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        """Mostra avatar do usuário"""
        if user is None:
            user = interaction.user
        
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title=f"🖼️ Avatar de {user.display_name}",
                color=discord.Color.blue()
            )
            
            avatar_url = user.display_avatar.url if user.display_avatar else user.default_avatar.url
            embed.set_image(url=avatar_url)
            embed.add_field(name="Link", value=f"[Clique aqui]({avatar_url})", inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando avatar: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar avatar.",
                ephemeral=True
            )
    
    @app_commands.command(name="roll", description="[BOT] Rola um dado")
    @app_commands.describe(sides="Número de lados do dado (padrão: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        """Rola um dado"""
        if sides < 2:
            await interaction.response.send_message(
                "❌ O dado precisa ter pelo menos 2 lados.",
                ephemeral=True
            )
            return
        
        if sides > 1000:
            await interaction.response.send_message(
                "❌ O dado pode ter no máximo 1000 lados.",
                ephemeral=True
            )
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Resultado do Dado",
            description=f"**{interaction.user.mention}** rolou um d{sides} e obteve: **{result}**",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="choose", description="[BOT] Escolhe uma opção aleatória")
    @app_commands.describe(options="Opções separadas por vírgula")
    async def choose(self, interaction: discord.Interaction, options: str):
        """Escolhe uma opção aleatória"""
        choices = [opt.strip() for opt in options.split(',') if opt.strip()]
        
        if len(choices) < 2:
            await interaction.response.send_message(
                "❌ Forneça pelo menos 2 opções separadas por vírgula.\n"
                "Exemplo: `/choose opção 1, opção 2, opção 3`",
                ephemeral=True
            )
            return
        
        if len(choices) > 20:
            await interaction.response.send_message(
                "❌ Máximo de 20 opções.",
                ephemeral=True
            )
            return
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Escolha Aleatória",
            description=f"**Opções:** {', '.join(choices)}\n\n"
                       f"**Escolhido:** {chosen}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="[BOT] Mostra a latência do bot")
    async def ping(self, interaction: discord.Interaction):
        """Mostra latência do bot"""
        latency = round(self.bot.latency * 1000, 2)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))

