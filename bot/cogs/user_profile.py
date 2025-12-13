"""
Cog para sistema de perfil de usuário
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class UserProfile(commands.Cog):
    """Sistema de perfil de usuário"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @app_commands.command(name="profile", description="Mostra perfil de um usuário do Discord")
    @app_commands.describe(user="Usuário para ver o perfil (deixe vazio para ver o seu)")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        """Mostra perfil do usuário"""
        if user is None:
            user = interaction.user
        
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title=f"👤 Perfil de {user.display_name}",
                color=user.color if user.color.value != 0 else discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
            
            # Informações básicas
            embed.add_field(name="Nome", value=user.name, inline=True)
            embed.add_field(name="ID", value=str(user.id), inline=True)
            embed.add_field(name="Mencionar", value=user.mention, inline=True)
            
            # Status
            status_emoji = {
                discord.Status.online: "🟢",
                discord.Status.idle: "🟡",
                discord.Status.dnd: "🔴",
                discord.Status.offline: "⚫"
            }
            embed.add_field(
                name="Status",
                value=f"{status_emoji.get(user.status, '⚫')} {user.status.name if user.status else 'offline'}",
                inline=True
            )
            
            # Datas
            if user.created_at:
                embed.add_field(
                    name="Conta criada",
                    value=f"<t:{int(user.created_at.timestamp())}:R>",
                    inline=True
                )
            
            if isinstance(user, discord.Member) and user.joined_at:
                embed.add_field(
                    name="Entrou no servidor",
                    value=f"<t:{int(user.joined_at.timestamp())}:R>",
                    inline=True
                )
            
            # Roles (se for membro)
            if isinstance(user, discord.Member):
                roles = [role.mention for role in user.roles if role.name != "@everyone"]
                if roles:
                    roles_str = ", ".join(roles[:10])  # Limitar a 10 roles
                    if len(roles) > 10:
                        roles_str += f" e mais {len(roles) - 10}"
                    embed.add_field(name="Roles", value=roles_str, inline=False)
            
            # Verificar se está autenticado no site
            from bot.core.auth_manager import AuthManager
            auth_manager = AuthManager(self.db)
            if auth_manager.is_authenticated(user.id):
                embed.add_field(
                    name="🔐 Autenticação",
                    value="✅ Autenticado no site",
                    inline=False
                )
            
            embed.set_footer(text=f"Bot PDL")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando profile: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar perfil.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(UserProfile(bot))

