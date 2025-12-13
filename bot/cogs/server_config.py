"""
Cog para configurações do servidor
"""

import logging
from typing import Optional, Union
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class TextChannelTransformer(app_commands.Transformer):
    """Transformer customizado para TextChannel que lida melhor com caracteres especiais"""
    
    async def transform(self, interaction: discord.Interaction, value) -> discord.TextChannel:
        """Transforma o valor em TextChannel"""
        # Se já é um TextChannel, retorna direto
        if isinstance(value, discord.TextChannel):
            return value
        
        channel_id = None
        
        # Se é um AppCommandChannel, pega o ID diretamente
        if isinstance(value, app_commands.AppCommandChannel):
            channel_id = value.id
        # Se é int, usa diretamente
        elif isinstance(value, int):
            channel_id = value
        # Se é string, pode ser ID, menção ou nome do canal
        elif isinstance(value, str):
            # Verifica se é uma menção de canal (formato <#ID>)
            if value.startswith('<#') and value.endswith('>'):
                # Extrai o ID da menção
                try:
                    channel_id = int(value[2:-1])
                except ValueError:
                    pass
            # Se começa com #, remove o # e tenta buscar por nome
            elif value.startswith('#'):
                channel_name = value[1:].strip()
                # Busca o canal por nome no guild (case-insensitive)
                guild = interaction.guild
                if guild:
                    # Primeiro tenta match exato (case-insensitive)
                    channel = discord.utils.find(lambda c: c.name.lower() == channel_name.lower(), guild.text_channels)
                    if not channel:
                        # Se não encontrou, tenta match parcial
                        channel = discord.utils.find(lambda c: channel_name.lower() in c.name.lower(), guild.text_channels)
                    if channel:
                        return channel
                # Se não encontrou, não define channel_id para tentar outras formas abaixo
            # Se não é menção nem começa com #, tenta converter para int (pode ser ID como string)
            else:
                try:
                    channel_id = int(value)
                except ValueError:
                    # Se não é um número, tenta buscar por nome
                    guild = interaction.guild
                    if guild:
                        # Primeiro tenta match exato (case-insensitive)
                        channel = discord.utils.find(lambda c: c.name.lower() == value.lower(), guild.text_channels)
                        if not channel:
                            # Se não encontrou, tenta match parcial
                            channel = discord.utils.find(lambda c: value.lower() in c.name.lower(), guild.text_channels)
                        if channel:
                            return channel
        # Tenta acessar como atributo (pode ser um objeto com .id)
        elif hasattr(value, 'id'):
            try:
                channel_id = int(value.id)
            except (ValueError, TypeError):
                pass
        
        if not channel_id:
            # Se não conseguiu obter o ID, levanta erro
            error_msg = f"Não foi possível obter o ID do canal do valor: {value} (tipo: {type(value)})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Busca o canal usando o ID
        # Primeiro tenta do cache do bot
        channel = interaction.client.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            return channel
        
        # Se não está em cache, tenta do guild
        guild = interaction.guild
        if guild:
            channel = guild.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                return channel
            
            # Tenta usar os dados resolved se disponíveis para criar o objeto
            if interaction.data and 'resolved' in interaction.data:
                resolved_channels = interaction.data['resolved'].get('channels', {})
                channel_data = resolved_channels.get(str(channel_id))
                if channel_data:
                    # Verifica se o tipo é text channel (type: 0)
                    if channel_data.get('type') == 0:
                        try:
                            # Garante que o ID está como string nos dados (requerido pelo discord.py)
                            channel_data_copy = channel_data.copy()
                            if 'id' in channel_data_copy and not isinstance(channel_data_copy['id'], str):
                                channel_data_copy['id'] = str(channel_data_copy['id'])
                            
                            # Tenta criar o objeto TextChannel a partir dos dados resolved
                            # Usando o state do client e os dados do resolved
                            state = interaction.client._connection
                            channel = discord.TextChannel(state=state, data=channel_data_copy, guild=guild)
                            
                            # Adiciona o canal ao cache do guild para uso futuro
                            guild._channels[channel_id] = channel
                            
                            return channel
                        except Exception as e:
                            # Se falhou, tenta fetch como fallback (pode falhar por permissão)
                            try:
                                channel = await guild.fetch_channel(channel_id)
                                if isinstance(channel, discord.TextChannel):
                                    return channel
                            except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                                pass
            
            # Última tentativa: fetch do Discord (se não tentamos ainda)
            if not channel:
                try:
                    channel = await guild.fetch_channel(channel_id)
                    if isinstance(channel, discord.TextChannel):
                        return channel
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    pass
        
        # Se chegou aqui, não conseguiu resolver
        # Mas se temos os dados em resolved, podemos pelo menos informar o usuário
        if interaction.data and 'resolved' in interaction.data:
            resolved_channels = interaction.data['resolved'].get('channels', {})
            if str(channel_id) in resolved_channels:
                error_msg = (
                    f"Não foi possível acessar o canal com ID {channel_id}. "
                    f"O bot pode não ter permissão para visualizar este canal. "
                    f"Verifique as permissões do bot no servidor."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        error_msg = f"Não foi possível encontrar o canal com ID {channel_id}"
        logger.error(error_msg)
        raise ValueError(error_msg)


class ServerConfig(commands.Cog):
    """Configurações do servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handler de erros para comandos deste cog"""
        if isinstance(error, app_commands.TransformerError):
            # Erro ao converter parâmetro (ex: canal com caracteres especiais)
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(
                        "❌ **Erro ao processar canal:**\n"
                        "O canal especificado não pôde ser encontrado ou convertido.\n\n"
                        "**Soluções:**\n"
                        "• Use a menção do canal (ex: #canal)\n"
                        "• Use o ID do canal\n"
                        "• Certifique-se de que o bot tem acesso ao canal\n"
                        "• Se o canal tem caracteres especiais, tente usar a menção ou ID",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        "❌ **Erro ao processar canal:**\n"
                        "O canal especificado não pôde ser encontrado ou convertido.\n\n"
                        "**Soluções:**\n"
                        "• Use a menção do canal (ex: #canal)\n"
                        "• Use o ID do canal\n"
                        "• Certifique-se de que o bot tem acesso ao canal\n"
                        "• Se o canal tem caracteres especiais, tente usar a menção ou ID",
                        ephemeral=True
                    )
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de erro: {e}", exc_info=True)
            return
        
        # Re-raise outros erros para o handler global
        raise error
    
    @app_commands.command(name="config", description="[BOT] Configurações do servidor")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):
        """Mostra configurações disponíveis"""
        config = await self.db.get_server_config(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="⚙️ Configurações do Servidor",
            description="Use os subcomandos para configurar o bot",
            color=discord.Color.blue()
        )
        
        # Função auxiliar para buscar canal
        async def get_channel_display(channel_id_str):
            """Busca um canal e retorna sua menção ou mensagem de erro"""
            if not channel_id_str:
                return "Não configurado"
            
            try:
                channel_id = int(channel_id_str)
                
                # Primeiro tenta do cache do bot
                channel = self.bot.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    return channel.mention
                
                # Se não está no cache, tenta do guild
                if interaction.guild:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel and isinstance(channel, discord.TextChannel):
                        return channel.mention
                    
                    # Última tentativa: fetch (pode falhar por permissão)
                    try:
                        channel = await interaction.guild.fetch_channel(channel_id)
                        if isinstance(channel, discord.TextChannel):
                            return channel.mention
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass
                
                # Se não encontrou, retorna o ID como fallback
                return f"<#{channel_id}> (ID: {channel_id})"
            except (ValueError, TypeError):
                return "ID inválido"
        
        # Mostrar configurações atuais
        feedback_channel = await get_channel_display(config.get('feedback_channel_id'))
        announcement_channel = await get_channel_display(config.get('announcement_channel_id'))
        log_channel = await get_channel_display(config.get('log_channel_id'))
        
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
        
        embed.set_footer(text="Use /config-set-channel e /config-set-notification para alterar as configurações")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="config-set-channel", description="[BOT] Define um canal de configuração")
    @app_commands.describe(
        setting="Tipo de canal a configurar",
        channel="Canal de texto (deixe vazio para remover)"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="Canal de Feedback", value="feedback_channel"),
        app_commands.Choice(name="Canal de Anúncios", value="announcement_channel"),
        app_commands.Choice(name="Canal de Logs", value="log_channel"),
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def config_set_channel(self, interaction: discord.Interaction, 
                                setting: app_commands.Choice[str],
                                channel: Optional[app_commands.Transform[discord.TextChannel, TextChannelTransformer]] = None):
        """Define um canal de configuração"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = await self.db.get_server_config(str(interaction.guild.id))
            setting_key = setting.value
            
            if not channel:
                # Remover canal
                config[setting_key + '_id'] = None
                await self.db.update_server_config(str(interaction.guild.id), config)
                await interaction.followup.send(
                    f"✅ Canal de {setting.name.lower()} removido.",
                    ephemeral=True
                )
                return
            
            # Validar que o canal é válido
            if not isinstance(channel, discord.TextChannel):
                await interaction.followup.send(
                    "❌ O canal deve ser um canal de texto.",
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
                
        except Exception as e:
            logger.error(f"Erro ao definir canal: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao definir canal. Tente novamente.",
                ephemeral=True
            )
    
    @app_commands.command(name="config-set-notification", description="[BOT] Ativa/desativa notificações")
    @app_commands.describe(
        setting="Tipo de notificação",
        enabled="Ativar ou desativar"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="Notificações de Bosses", value="boss_notifications"),
        app_commands.Choice(name="Notificações de Cercos", value="siege_notifications"),
        app_commands.Choice(name="Notificações de Olimpíada", value="olympiad_notifications"),
        app_commands.Choice(name="Notificações de Entrada de Membros", value="member_join_notifications"),
        app_commands.Choice(name="Notificações de Saída de Membros", value="member_leave_notifications"),
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def config_set_notification(self, interaction: discord.Interaction,
                                      setting: app_commands.Choice[str],
                                      enabled: bool):
        """Ativa ou desativa uma notificação"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = await self.db.get_server_config(str(interaction.guild.id))
            setting_key = setting.value
            
            config[setting_key] = enabled
            status = "ativadas" if enabled else "desativadas"
            
            await self.db.update_server_config(str(interaction.guild.id), config)
            await interaction.followup.send(
                f"✅ Notificações de {setting.name.lower()} {status}.",
                ephemeral=True
            )
                
        except Exception as e:
            logger.error(f"Erro ao definir notificação: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao definir notificação. Tente novamente.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ServerConfig(bot))

