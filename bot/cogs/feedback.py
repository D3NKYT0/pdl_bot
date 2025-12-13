"""
Cog para sistema de feedback e sugestões
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)


class Feedback(commands.Cog):
    """Sistema de feedback e sugestões"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="feedback", description="Envia feedback, sugestão ou reporta um bug")
    @app_commands.describe(message="Sua mensagem de feedback, sugestão ou reporte")
    async def feedback(self, interaction: discord.Interaction, message: str):
        """Envia feedback para os desenvolvedores"""
        # Limitar tamanho da mensagem
        if len(message) > 2000:
            await interaction.response.send_message(
                "❌ Sua mensagem é muito longa. Por favor, envie em partes menores (máximo 2000 caracteres).",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Salvar no banco de dados
            server_data = await self.db.get_server_by_discord_id(str(interaction.guild.id))
            server_name = server_data.get('server_name') if server_data else interaction.guild.name
            
            feedback_data = await self.db.save_feedback(
                str(interaction.user.id),
                str(interaction.guild.id),
                message,
                server_name
            )
            
            # Tentar enviar para canal de feedback configurado
            config = await self.db.get_server_config(str(interaction.guild.id))
            feedback_channel_id = config.get('feedback_channel_id')
            
            if feedback_channel_id:
                try:
                    feedback_channel = self.bot.get_channel(int(feedback_channel_id))
                    if feedback_channel:
                        embed = discord.Embed(
                            title="💬 Novo Feedback",
                            description=message,
                            color=discord.Color.blue(),
                            timestamp=datetime.utcnow()
                        )
                        embed.add_field(name="Servidor", value=interaction.guild.name, inline=True)
                        embed.add_field(name="ID do Servidor", value=str(interaction.guild.id), inline=True)
                        embed.add_field(name="Usuário", value=f"{interaction.user.name} ({interaction.user.id})", inline=False)
                        embed.set_thumbnail(url=interaction.user.display_avatar.url)
                        embed.set_footer(text="Bot PDL - Sistema de Feedback")
                        
                        await feedback_channel.send(embed=embed)
                except Exception as e:
                    logger.warning(f"Erro ao enviar feedback para canal: {e}")
            
            await interaction.followup.send(
                "✅ **Feedback enviado com sucesso!**\n\n"
                "Obrigado por contribuir para melhorar o bot. Sua opinião é muito importante!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erro no comando feedback: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao enviar feedback. Tente novamente mais tarde.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Feedback(bot))

