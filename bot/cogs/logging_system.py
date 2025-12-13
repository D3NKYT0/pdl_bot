"""
Cog para sistema de logs e auditoria
"""

import logging
import discord
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)


class LoggingSystem(commands.Cog):
    """Sistema de logs e auditoria do servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def send_log(self, guild_id: int, embed: discord.Embed):
        """Envia log para o canal configurado"""
        try:
            config = await self.db.get_server_config(str(guild_id))
            log_channel_id = config.get('log_channel_id')
            
            if not log_channel_id:
                return
            
            # Buscar canal de forma robusta
            channel_id = int(log_channel_id)
            log_channel = self.bot.get_channel(channel_id)
            
            # Se não está no cache do bot, tenta buscar do guild
            if not log_channel:
                guild = self.bot.get_guild(guild_id)
                if guild:
                    log_channel = guild.get_channel(channel_id)
                    if not log_channel:
                        # Última tentativa: fetch
                        try:
                            log_channel = await guild.fetch_channel(channel_id)
                        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                            pass
            
            if log_channel and isinstance(log_channel, discord.TextChannel):
                await log_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Erro ao enviar log: {e}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log quando mensagem é deletada"""
        if not message.guild or message.author.bot:
            return
        
        config = await self.db.get_server_config(str(message.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="🗑️ Mensagem Deletada",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Autor", value=f"{message.author.mention} ({message.author.id})", inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        
        if message.content:
            content = message.content[:1000]  # Limitar tamanho
            embed.add_field(name="Conteúdo", value=content or "*Sem conteúdo*", inline=False)
        
        embed.set_footer(text=f"ID da Mensagem: {message.id}")
        await self.send_log(message.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log quando mensagem é editada"""
        if not after.guild or after.author.bot or before.content == after.content:
            return
        
        config = await self.db.get_server_config(str(after.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="✏️ Mensagem Editada",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Autor", value=f"{after.author.mention} ({after.author.id})", inline=True)
        embed.add_field(name="Canal", value=after.channel.mention, inline=True)
        embed.add_field(name="Antes", value=before.content[:500] or "*Sem conteúdo*", inline=False)
        embed.add_field(name="Depois", value=after.content[:500] or "*Sem conteúdo*", inline=False)
        embed.set_footer(text=f"ID da Mensagem: {after.id}")
        await self.send_log(after.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log quando membro é banido"""
        config = await self.db.get_server_config(str(guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="🔨 Membro Banido",
            color=discord.Color.dark_red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Usuário", value=f"{user.name} ({user.id})", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        await self.send_log(guild.id, embed)
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log quando membro é desbanido"""
        config = await self.db.get_server_config(str(guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="✅ Membro Desbanido",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Usuário", value=f"{user.name} ({user.id})", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url if user.display_avatar else None)
        await self.send_log(guild.id, embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Log quando canal é criado"""
        config = await self.db.get_server_config(str(channel.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="➕ Canal Criado",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Canal", value=f"{channel.mention} ({channel.name})", inline=True)
        embed.add_field(name="Tipo", value=channel.type.name, inline=True)
        await self.send_log(channel.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Log quando canal é deletado"""
        config = await self.db.get_server_config(str(channel.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="➖ Canal Deletado",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Canal", value=f"{channel.name} (ID: {channel.id})", inline=True)
        embed.add_field(name="Tipo", value=channel.type.name, inline=True)
        await self.send_log(channel.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Log quando role é criada"""
        config = await self.db.get_server_config(str(role.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="➕ Role Criada",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Role", value=f"{role.mention} ({role.name})", inline=True)
        embed.add_field(name="Cor", value=str(role.color), inline=True)
        await self.send_log(role.guild.id, embed)
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Log quando role é deletada"""
        config = await self.db.get_server_config(str(role.guild.id))
        if not config.get('log_channel_id'):
            return
        
        embed = discord.Embed(
            title="➖ Role Deletada",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Role", value=f"{role.name} (ID: {role.id})", inline=True)
        await self.send_log(role.guild.id, embed)


async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))

