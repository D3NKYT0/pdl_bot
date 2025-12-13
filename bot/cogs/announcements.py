"""
Cog para sistema de anúncios
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)


class Announcements(commands.Cog):
    """Sistema de anúncios"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="announce", description="Faz um anúncio no canal configurado")
    @app_commands.describe(message="Mensagem do anúncio")
    @app_commands.default_permissions(manage_guild=True)
    async def announce(self, interaction: discord.Interaction, message: str):
        """Faz um anúncio"""
        if len(message) > 2000:
            await interaction.response.send_message(
                "❌ Mensagem muito longa (máximo 2000 caracteres).",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = await self.db.get_server_config(str(interaction.guild.id))
            announcement_channel_id = config.get('announcement_channel_id')
            
            if not announcement_channel_id:
                await interaction.followup.send(
                    "❌ Canal de anúncios não configurado. Use `/config-set` para configurar.",
                    ephemeral=True
                )
                return
            
            announcement_channel = self.bot.get_channel(int(announcement_channel_id))
            
            if not announcement_channel:
                await interaction.followup.send(
                    "❌ Canal de anúncios não encontrado. Verifique a configuração.",
                    ephemeral=True
                )
                return
            
            # Criar embed do anúncio
            embed = discord.Embed(
                title="📢 Anúncio",
                description=message,
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text=f"Servidor: {interaction.guild.name}")
            
            # Enviar anúncio
            await announcement_channel.send(embed=embed)
            
            await interaction.followup.send(
                f"✅ Anúncio enviado com sucesso em {announcement_channel.mention}!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erro no comando announce: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao enviar anúncio. Tente novamente.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Announcements(bot))

