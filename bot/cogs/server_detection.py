"""
Cog para detecção e registro de servidores
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class ServerDetection(commands.Cog):
    """Comandos para detectar e registrar servidores"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="register", description="[PAINEL] Registra este servidor com um domínio do site PDL")
    @app_commands.describe(domain="Domínio do site (ex: pdl.denky.dev.br)")
    async def register(self, interaction: discord.Interaction, domain: str):
        """Registra o servidor Discord com um domínio do site"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Verificar se já está registrado
            existing = await self.db.get_server_by_discord_id(str(interaction.guild.id))
            
            if existing:
                await interaction.followup.send(
                    f"❌ Este servidor já está registrado com o domínio: `{existing['site_domain']}`\n"
                    f"Use `/unregister` para remover o registro atual.",
                    ephemeral=True
                )
                return
            
            # Registrar servidor
            server_data = await self.db.register_server(
                discord_guild_id=str(interaction.guild.id),
                site_domain=domain,
                server_name=interaction.guild.name
            )
            
            # Verificar se a API está acessível
            from bot.core.site_client import SiteClient
            client = SiteClient(domain)
            is_online = await client.check_health()
            await client.close()
            
            if is_online:
                status_emoji = "✅"
                status_msg = "API acessível"
            else:
                status_emoji = "⚠️"
                status_msg = "API não acessível (verifique o domínio)"
            
            await interaction.followup.send(
                f"{status_emoji} **Servidor registrado com sucesso!**\n\n"
                f"**Domínio:** `{server_data['site_domain']}`\n"
                f"**Status:** {status_msg}\n\n"
                f"Agora você pode usar comandos como `/online`, `/top-pvp`, etc.",
                ephemeral=True
            )
            
            logger.info(f"Servidor {interaction.guild.name} registrado: {domain}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar servidor: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao registrar servidor: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="unregister", description="[PAINEL] Remove o registro deste servidor")
    async def unregister(self, interaction: discord.Interaction):
        """Remove o registro do servidor"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            server_data = await self.db.get_server_by_discord_id(str(interaction.guild.id))
            
            if not server_data:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            removed = await self.db.unregister_server(str(interaction.guild.id))
            
            if removed:
                await interaction.followup.send(
                    f"✅ **Registro removido com sucesso!**\n\n"
                    f"O servidor não está mais vinculado ao domínio `{server_data['site_domain']}`.",
                    ephemeral=True
                )
                logger.info(f"Servidor {interaction.guild.name} desregistrado")
            else:
                await interaction.followup.send(
                    "❌ Erro ao remover registro.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erro ao remover registro: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao remover registro: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="status", description="[PAINEL] Verifica o status do registro deste servidor")
    async def status(self, interaction: discord.Interaction):
        """Verifica o status do registro"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            server_data = await self.db.get_server_by_discord_id(str(interaction.guild.id))
            
            if not server_data:
                await interaction.followup.send(
                    "❌ **Este servidor não está registrado.**\n\n"
                    "Use `/register <domínio>` para registrar este servidor com um site PDL.",
                    ephemeral=True
                )
                return
            
            # Verificar se a API está acessível
            from bot.core.site_client import SiteClient
            client = SiteClient(server_data['site_domain'])
            is_online = await client.check_health()
            await client.close()
            
            status_emoji = "✅" if is_online else "⚠️"
            status_text = "Online" if is_online else "Offline"
            
            embed = discord.Embed(
                title="📊 Status do Servidor",
                color=discord.Color.green() if is_online else discord.Color.orange()
            )
            embed.add_field(name="Domínio", value=f"`{server_data['site_domain']}`", inline=False)
            embed.add_field(name="Status da API", value=f"{status_emoji} {status_text}", inline=False)
            embed.add_field(name="Ativo", value="✅ Sim" if server_data.get('is_active', True) else "❌ Não", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao verificar status: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ServerDetection(bot))
