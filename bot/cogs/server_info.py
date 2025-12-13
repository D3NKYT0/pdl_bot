"""
Cog para exibir informações do servidor do jogo
"""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class ServerInfo(commands.Cog):
    """Comandos para exibir informações do servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def _get_site_client(self, guild_id: int):
        """Obtém o cliente do site para o servidor"""
        server_data = await self.db.get_server_by_discord_id(str(guild_id))
        
        if not server_data:
            return None
        
        return await self.bot.get_site_client(server_data['site_domain'])
    
    @app_commands.command(name="online", description="Mostra quantos jogadores estão online")
    async def online(self, interaction: discord.Interaction):
        """Mostra jogadores online"""
        await interaction.response.defer()
        
        try:
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.get_players_online()
            
            if not data:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do servidor. Verifique se a API está acessível.",
                    ephemeral=True
                )
                return
            
            online_count = data.get('online_count', 0)
            real_players = data.get('real_players', online_count)
            
            embed = discord.Embed(
                title="👥 Jogadores Online",
                description=f"**{online_count}** jogadores online agora",
                color=discord.Color.green()
            )
            embed.add_field(name="Jogadores Reais", value=f"{real_players}", inline=True)
            embed.set_footer(text=f"Fonte: {client.domain}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar jogadores online: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao buscar dados: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="top-pvp", description="Mostra o ranking de PvP")
    @app_commands.describe(limit="Número de jogadores (padrão: 10)")
    async def top_pvp(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra top PvP"""
        await interaction.response.defer()
        
        try:
            if limit > 20:
                limit = 20
            if limit < 1:
                limit = 10
            
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.get_top_pvp(limit)
            
            # Aceita tanto lista direta quanto dict com 'results' (compatibilidade)
            if isinstance(data, list):
                results = data[:limit]
            elif isinstance(data, dict) and 'results' in data:
                results = data['results'][:limit]
            else:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do ranking.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="⚔️ Top PvP",
                color=discord.Color.red()
            )
            
            description = ""
            for i, player in enumerate(results, 1):
                char_name = player.get('char_name', 'N/A')
                pvp_count = player.get('pvpkills', player.get('pvp_count', 0))
                description += f"**{i}.** {char_name} - {pvp_count} PvPs\n"
            
            if not description:
                description = "Nenhum dado disponível"
            
            embed.description = description
            embed.set_footer(text=f"Fonte: {client.domain}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar top PvP: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao buscar dados: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="top-pk", description="Mostra o ranking de PK")
    @app_commands.describe(limit="Número de jogadores (padrão: 10)")
    async def top_pk(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra top PK"""
        await interaction.response.defer()
        
        try:
            if limit > 20:
                limit = 20
            if limit < 1:
                limit = 10
            
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.get_top_pk(limit)
            
            # Aceita tanto lista direta quanto dict com 'results' (compatibilidade)
            if isinstance(data, list):
                results = data[:limit]
            elif isinstance(data, dict) and 'results' in data:
                results = data['results'][:limit]
            else:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do ranking.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🔪 Top PK",
                color=discord.Color.dark_red()
            )
            
            description = ""
            for i, player in enumerate(results, 1):
                char_name = player.get('char_name', 'N/A')
                pk_count = player.get('pkkills', player.get('pk_count', 0))
                description += f"**{i}.** {char_name} - {pk_count} PKs\n"
            
            if not description:
                description = "Nenhum dado disponível"
            
            embed.description = description
            embed.set_footer(text=f"Fonte: {client.domain}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar top PK: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao buscar dados: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="top-level", description="Mostra o ranking de nível")
    @app_commands.describe(limit="Número de jogadores (padrão: 10)")
    async def top_level(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra top nível"""
        await interaction.response.defer()
        
        try:
            if limit > 20:
                limit = 20
            if limit < 1:
                limit = 10
            
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.get_top_level(limit)
            
            # Aceita tanto lista direta quanto dict com 'results' (compatibilidade)
            if isinstance(data, list):
                results = data[:limit]
            elif isinstance(data, dict) and 'results' in data:
                results = data['results'][:limit]
            else:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do ranking.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📈 Top Nível",
                color=discord.Color.blue()
            )
            
            description = ""
            for i, player in enumerate(results, 1):
                char_name = player.get('char_name', 'N/A')
                level = player.get('level', 0)
                description += f"**{i}.** {char_name} - Nível {level}\n"
            
            if not description:
                description = "Nenhum dado disponível"
            
            embed.description = description
            embed.set_footer(text=f"Fonte: {client.domain}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar top nível: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao buscar dados: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="search", description="Busca um personagem")
    @app_commands.describe(character_name="Nome do personagem")
    async def search(self, interaction: discord.Interaction, character_name: str):
        """Busca um personagem"""
        await interaction.response.defer()
        
        try:
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.search_character(character_name)
            
            # Aceita tanto lista quanto dict (compatibilidade)
            if isinstance(data, list):
                if len(data) == 0:
                    await interaction.followup.send(
                        f"❌ Personagem `{character_name}` não encontrado.",
                        ephemeral=True
                    )
                    return
                # Pega o primeiro resultado se for lista
                data = data[0]
            elif not data or not isinstance(data, dict):
                await interaction.followup.send(
                    f"❌ Personagem `{character_name}` não encontrado.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🔍 {data.get('char_name', character_name)}",
                color=discord.Color.blue()
            )
            
            if 'level' in data:
                embed.add_field(name="Nível", value=str(data['level']), inline=True)
            if 'class_name' in data:
                embed.add_field(name="Classe", value=data['class_name'], inline=True)
            if 'clan_name' in data:
                embed.add_field(name="Clã", value=data['clan_name'], inline=True)
            
            embed.set_footer(text=f"Fonte: {client.domain}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar personagem: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao buscar personagem: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
