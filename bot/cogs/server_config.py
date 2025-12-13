"""
Cog para configurações do servidor
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class ServerConfig(commands.Cog):
    """Configurações do servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="config", description="Configurações do servidor")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):
        """Mostra configurações disponíveis"""
        config = await self.db.get_server_config(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="⚙️ Configurações do Servidor",
            description="Use os subcomandos para configurar o bot",
            color=discord.Color.blue()
        )
        
        # Mostrar configurações atuais
        feedback_channel = "Não configurado"
        if config.get('feedback_channel_id'):
            channel = self.bot.get_channel(int(config['feedback_channel_id']))
            feedback_channel = channel.mention if channel else "Canal não encontrado"
        
        announcement_channel = "Não configurado"
        if config.get('announcement_channel_id'):
            channel = self.bot.get_channel(int(config['announcement_channel_id']))
            announcement_channel = channel.mention if channel else "Canal não encontrado"
        
        log_channel = "Não configurado"
        if config.get('log_channel_id'):
            channel = self.bot.get_channel(int(config['log_channel_id']))
            log_channel = channel.mention if channel else "Canal não encontrado"
        
        embed.add_field(
            name="📝 Canais",
            value=f"**Feedback:** {feedback_channel}\n"
                  f"**Anúncios:** {announcement_channel}\n"
                  f"**Logs:** {log_channel}",
            inline=False
        )
        
        embed.add_field(
            name="🔔 Notificações",
            value=f"**Bosses:** {'✅' if config.get('boss_notifications') else '❌'}\n"
                  f"**Cercos:** {'✅' if config.get('siege_notifications') else '❌'}\n"
                  f"**Olimpíada:** {'✅' if config.get('olympiad_notifications') else '❌'}\n"
                  f"**Membros (Entrada):** {'✅' if config.get('member_join_notifications') else '❌'}\n"
                  f"**Membros (Saída):** {'✅' if config.get('member_leave_notifications') else '❌'}",
            inline=False
        )
        
        embed.set_footer(text="Use /config-set para alterar as configurações")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="config-set", description="Define uma configuração do servidor")
    @app_commands.describe(
        setting="Configuração a alterar",
        channel="Canal (para configurações de canal)",
        enabled="Ativar/desativar (para notificações)"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="Canal de Feedback", value="feedback_channel"),
        app_commands.Choice(name="Canal de Anúncios", value="announcement_channel"),
        app_commands.Choice(name="Canal de Logs", value="log_channel"),
        app_commands.Choice(name="Notificações de Bosses", value="boss_notifications"),
        app_commands.Choice(name="Notificações de Cercos", value="siege_notifications"),
        app_commands.Choice(name="Notificações de Olimpíada", value="olympiad_notifications"),
        app_commands.Choice(name="Notificações de Entrada de Membros", value="member_join_notifications"),
        app_commands.Choice(name="Notificações de Saída de Membros", value="member_leave_notifications"),
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def config_set(self, interaction: discord.Interaction, 
                        setting: app_commands.Choice[str], 
                        channel: discord.TextChannel = None,
                        enabled: bool = None):
        """Define uma configuração"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = await self.db.get_server_config(str(interaction.guild.id))
            setting_key = setting.value
            
            # Configurações de canal
            if setting_key.endswith('_channel'):
                if not channel:
                    # Remover canal
                    config[setting_key + '_id'] = None
                    await self.db.update_server_config(str(interaction.guild.id), config)
                    await interaction.followup.send(
                        f"✅ Canal de {setting.name.lower()} removido.",
                        ephemeral=True
                    )
                    return
                
                if channel.guild.id != interaction.guild.id:
                    await interaction.followup.send(
                        "❌ O canal deve estar neste servidor.",
                        ephemeral=True
                    )
                    return
                
                config[setting_key + '_id'] = str(channel.id)
                await self.db.update_server_config(str(interaction.guild.id), config)
                await interaction.followup.send(
                    f"✅ Canal de {setting.name.lower()} definido para {channel.mention}",
                    ephemeral=True
                )
            
            # Configurações booleanas (notificações)
            elif setting_key.endswith('_notifications'):
                if enabled is None:
                    await interaction.followup.send(
                        "❌ Use `enabled: true` ou `enabled: false` para ativar/desativar.",
                        ephemeral=True
                    )
                    return
                
                config[setting_key] = enabled
                status = "ativadas" if enabled else "desativadas"
                
                await self.db.update_server_config(str(interaction.guild.id), config)
                await interaction.followup.send(
                    f"✅ Notificações de {setting.name.lower()} {status}.",
                    ephemeral=True
                )
            
            else:
                await interaction.followup.send(
                    "❌ Configuração não reconhecida.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erro ao definir configuração: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao definir configuração. Tente novamente.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ServerConfig(bot))

