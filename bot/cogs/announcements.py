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
    
    @app_commands.command(name="announce", description="[BOT] Faz um anúncio no canal configurado")
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
                    "❌ Canal de anúncios não configurado. Use `/config-set-channel` para configurar.",
                    ephemeral=True
                )
                return
            
            # Buscar canal de forma robusta
            announcement_channel = None
            channel_id = int(announcement_channel_id)
            
            # Primeiro tenta do cache do bot
            announcement_channel = self.bot.get_channel(channel_id)
            if announcement_channel and isinstance(announcement_channel, discord.TextChannel):
                logger.debug(f"Canal de anúncios {channel_id} encontrado no cache do bot")
            elif interaction.guild:
                # Tenta do cache do guild
                announcement_channel = interaction.guild.get_channel(channel_id)
                if announcement_channel and isinstance(announcement_channel, discord.TextChannel):
                    logger.debug(f"Canal de anúncios {channel_id} encontrado no cache do guild")
                else:
                    # Última tentativa: fetch
                    try:
                        announcement_channel = await interaction.guild.fetch_channel(channel_id)
                        if isinstance(announcement_channel, discord.TextChannel):
                            logger.debug(f"Canal de anúncios {channel_id} obtido via fetch")
                    except discord.NotFound:
                        logger.warning(f"Canal de anúncios {channel_id} não encontrado (404)")
                    except discord.Forbidden:
                        logger.warning(f"Sem permissão para acessar canal de anúncios {channel_id} (403)")
                        # Mesmo sem permissão para fetch, podemos tentar enviar usando o ID
                        # Criar um objeto TextChannel mínimo usando os dados conhecidos
                        try:
                            state = self.bot._connection
                            channel_data = {
                                'id': str(channel_id),
                                'type': 0,  # Text channel
                                'guild_id': str(interaction.guild.id),
                                'name': f'canal-{channel_id}',
                                'position': 0,
                                'permission_overwrites': [],
                                'topic': None,
                                'rate_limit_per_user': 0,
                                'nsfw': False,
                                'parent_id': None,
                                'last_message_id': None,
                                'flags': 0
                            }
                            announcement_channel = discord.TextChannel(state=state, data=channel_data, guild=interaction.guild)
                            logger.info(f"Criado objeto TextChannel para {channel_id} sem fetch (sem permissão)")
                        except Exception as create_error:
                            logger.error(f"Erro ao criar objeto TextChannel: {create_error}", exc_info=True)
                            # Se não conseguir criar, tenta enviar diretamente usando o ID
                            # Isso pode funcionar se o bot tiver permissão de enviar mas não de ver
                            try:
                                # Tenta obter o canal via API direta
                                channel = interaction.guild.get_channel(channel_id)
                                if channel:
                                    announcement_channel = channel
                                    logger.info(f"Canal {channel_id} obtido via get_channel após erro 403")
                            except:
                                pass
                    except discord.HTTPException as e:
                        logger.warning(f"Erro HTTP ao buscar canal de anúncios {channel_id}: {e}")
            
            if not announcement_channel or not isinstance(announcement_channel, discord.TextChannel):
                # Se chegou aqui, não conseguiu encontrar o canal
                # Tenta enviar mesmo assim usando o ID diretamente (pode funcionar se tiver permissão de enviar)
                try:
                    # Tenta obter o canal novamente do guild (pode estar no cache agora)
                    if interaction.guild:
                        announcement_channel = interaction.guild.get_channel(channel_id)
                        if announcement_channel and isinstance(announcement_channel, discord.TextChannel):
                            logger.info(f"Canal {channel_id} encontrado no segundo try")
                        else:
                            # Última tentativa: criar objeto mínimo e tentar enviar
                            state = self.bot._connection
                            channel_data = {
                                'id': str(channel_id),
                                'type': 0,
                                'guild_id': str(interaction.guild.id),
                                'name': 'canal',
                                'position': 0,
                                'permission_overwrites': [],
                                'topic': None,
                                'rate_limit_per_user': 0,
                                'nsfw': False,
                                'parent_id': None,
                                'last_message_id': None,
                                'flags': 0
                            }
                            announcement_channel = discord.TextChannel(state=state, data=channel_data, guild=interaction.guild)
                            logger.info(f"Tentando usar canal {channel_id} criado artificialmente")
                except Exception as e:
                    logger.error(f"Erro ao tentar criar canal artificialmente: {e}", exc_info=True)
                
                # Se ainda não tem canal, mostra erro
                if not announcement_channel or not isinstance(announcement_channel, discord.TextChannel):
                    error_msg = (
                        f"❌ Canal de anúncios não encontrado (ID: {channel_id}).\n\n"
                        f"**Possíveis causas:**\n"
                        f"• O canal foi deletado\n"
                        f"• O bot não tem permissão para **ver** o canal (View Channel)\n"
                        f"• O ID do canal está incorreto\n\n"
                        f"**Solução:**\n"
                        f"1. Verifique se o bot tem permissão 'Ver Canais' no canal\n"
                        f"2. Verifique se o canal ainda existe\n"
                        f"3. Use `/config-set-channel` para reconfigurar o canal"
                    )
                    await interaction.followup.send(error_msg, ephemeral=True)
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
            try:
                await announcement_channel.send(embed=embed)
                await interaction.followup.send(
                    f"✅ Anúncio enviado com sucesso em {announcement_channel.mention}!",
                    ephemeral=True
                )
            except discord.Forbidden as e:
                error_code = getattr(e, 'code', None)
                if error_code == 50001:  # Missing Access
                    error_msg = (
                        f"❌ **Erro: Sem permissão para enviar mensagens no canal**\n\n"
                        f"O bot não tem permissão para enviar mensagens no canal de anúncios.\n\n"
                        f"**Permissões necessárias:**\n"
                        f"• Ver Canais (View Channel)\n"
                        f"• Enviar Mensagens (Send Messages)\n"
                        f"• Incorporar Links (Embed Links)\n\n"
                        f"Verifique as permissões do bot no canal <#{channel_id}> e tente novamente."
                    )
                else:
                    error_msg = (
                        f"❌ **Erro ao enviar anúncio**\n\n"
                        f"O bot não tem permissão para enviar mensagens no canal.\n"
                        f"Verifique as permissões do bot no canal de anúncios."
                    )
                logger.error(f"Erro 403 ao enviar anúncio no canal {channel_id}: {e}")
                await interaction.followup.send(error_msg, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro no comando announce: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao enviar anúncio. Tente novamente.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Announcements(bot))

