"""
Cog para sistema de notificações automáticas
"""

import logging
import discord
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)


class Notifications(commands.Cog):
    """Sistema de notificações automáticas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def send_notification(self, guild_id: int, embed: discord.Embed, notification_type: str):
        """Envia notificação se estiver habilitada"""
        try:
            config = await self.db.get_server_config(str(guild_id))
            
            # Verificar se notificação está habilitada
            if not config.get(f'{notification_type}_notifications', False):
                return
            
            # Usar canal de anúncios ou logs como fallback
            channel_id = config.get('announcement_channel_id') or config.get('log_channel_id')
            
            if not channel_id:
                return
            
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Notifica quando membro entra"""
        config = await self.db.get_server_config(str(member.guild.id))
        
        if not config.get('member_join_notifications', False):
            return
        
        embed = discord.Embed(
            title="👋 Novo Membro",
            description=f"{member.mention} entrou no servidor!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Usuário", value=f"{member.name} ({member.id})", inline=True)
        embed.add_field(name="Conta criada", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        
        await self.send_notification(member.guild.id, embed, 'member_join')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Notifica quando membro sai"""
        config = await self.db.get_server_config(str(member.guild.id))
        
        if not config.get('member_leave_notifications', False):
            return
        
        embed = discord.Embed(
            title="👋 Membro Saiu",
            description=f"{member.name} saiu do servidor.",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Usuário", value=f"{member.name} ({member.id})", inline=True)
        if member.joined_at:
            embed.add_field(name="Entrou em", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else None)
        
        await self.send_notification(member.guild.id, embed, 'member_leave')
    
    # Métodos auxiliares para notificações de bosses, cercos, etc.
    # Estes serão chamados por outros cogs quando necessário
    
    async def notify_boss_spawn(self, guild_id: int, boss_name: str, location: str):
        """Notifica sobre spawn de boss"""
        embed = discord.Embed(
            title="🐉 Boss Spawnou!",
            description=f"**{boss_name}** está vivo!",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Localização", value=location, inline=True)
        await self.send_notification(guild_id, embed, 'boss')
    
    async def notify_siege(self, guild_id: int, castle_name: str, status: str):
        """Notifica sobre cerco"""
        embed = discord.Embed(
            title="🏰 Cerco",
            description=f"**{castle_name}**: {status}",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow()
        )
        await self.send_notification(guild_id, embed, 'siege')
    
    async def notify_olympiad(self, guild_id: int, message: str):
        """Notifica sobre olimpíada"""
        embed = discord.Embed(
            title="🏆 Olimpíada",
            description=message,
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        await self.send_notification(guild_id, embed, 'olympiad')


async def setup(bot):
    await bot.add_cog(Notifications(bot))

