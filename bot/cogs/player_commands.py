"""
Cog com comandos para jogadores interagirem com a API do site
Inclui bosses, olimpíada, cercos, clãs, leilão e comandos autenticados
"""

import logging
import time
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from typing import Optional
from bot.core.rate_limiter import rate_limiter
from bot.core.auth_manager import AuthManager

logger = logging.getLogger(__name__)


class PlayerCommands(commands.Cog):
    """Comandos para jogadores interagirem com o servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.auth_manager = AuthManager(bot.db)
    
    async def _get_site_client(self, guild_id: int):
        """Obtém o cliente do site para o servidor"""
        server_data = await self.db.get_server_by_discord_id(str(guild_id))
        
        if not server_data:
            return None, None
        
        client = await self.bot.get_site_client(server_data['site_domain'])
        return client, server_data['site_domain']
    
    async def _check_rate_limit(self, interaction: discord.Interaction, command: str) -> bool:
        """Verifica rate limit e responde se excedido"""
        if not rate_limiter.is_allowed(interaction.user.id, command):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, command)
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return False
        return True
    
    def _sanitize_input(self, text: str, max_length: int = 50) -> str:
        """Sanitiza input do usuário"""
        # Remove caracteres perigosos e limita tamanho
        text = text.strip()[:max_length]
        # Remove caracteres de controle
        text = ''.join(char for char in text if char.isprintable())
        return text
    
    def _format_time(self, timestamp: Optional[str]) -> str:
        """Formata timestamp para exibição"""
        if not timestamp:
            return "N/A"
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return f"<t:{int(dt.timestamp())}:R>"
        except:
            return timestamp
    
    # ==================== COMANDOS DE BOSSES ====================
    
    @app_commands.command(name="bosses", description="[PAINEL] Mostra status dos Grand Bosses")
    async def bosses(self, interaction: discord.Interaction):
        """Mostra status dos Grand Bosses"""
        if not await self._check_rate_limit(interaction, "bosses"):
            import time
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "bosses")
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            data = await client.get_grandboss_status()
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados dos bosses.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🐉 Status dos Grand Bosses",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            
            # Limita a 10 bosses para não exceder limite do embed
            for boss in data[:10]:
                status = "🟢 Vivo" if boss.get('is_alive') else "🔴 Morto"
                respawn_time = boss.get('respawn_time', '-')
                # Se respawn_time é "-", não tenta formatar
                if respawn_time and respawn_time != '-':
                    respawn = self._format_time(respawn_time)
                else:
                    respawn = respawn_time
                location = boss.get('location', 'N/A')
                
                embed.add_field(
                    name=f"{boss.get('boss_name', 'Unknown')}",
                    value=f"**Status:** {status}\n**Respawn:** {respawn}\n**Local:** {location}",
                    inline=True
                )
            
            if len(data) > 10:
                embed.set_footer(text=f"Mostrando 10 de {len(data)} bosses")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando bosses: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações dos bosses.",
                ephemeral=True
            )
    
    @app_commands.command(name="boss-jewel", description="[PAINEL] Busca localização de Boss Jewels")
    @app_commands.describe(jewel_ids="IDs dos jewels separados por vírgula (ex: 6656,6657)")
    async def boss_jewel(self, interaction: discord.Interaction, jewel_ids: str):
        """Busca localização de Boss Jewels"""
        if not await self._check_rate_limit(interaction, "boss_jewel"):
            return
        
        await interaction.response.defer()
        
        try:
            # Valida e sanitiza IDs
            try:
                ids = [int(id.strip()) for id in jewel_ids.split(',')]
                if len(ids) > 10:
                    await interaction.followup.send(
                        "❌ Máximo de 10 jewels por vez.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.followup.send(
                    "❌ IDs inválidos. Use números separados por vírgula (ex: 6656,6657).",
                    ephemeral=True
                )
                return
            
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_boss_jewel_locations(ids)
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados dos jewels.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="💎 Localização dos Boss Jewels",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            for jewel in data:
                respawn = self._format_time(jewel.get('respawn_time'))
                location = jewel.get('location', 'N/A')
                coords = jewel.get('coordinates', 'N/A')
                
                embed.add_field(
                    name=f"{jewel.get('jewel_name', 'Unknown')} (ID: {jewel.get('jewel_id')})",
                    value=f"**Local:** {location}\n**Coords:** {coords}\n**Respawn:** {respawn}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando boss_jewel: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações dos jewels.",
                ephemeral=True
            )
    
    # ==================== COMANDOS DE OLIMPÍADA ====================
    
    @app_commands.command(name="olympiad", description="[PAINEL] Mostra ranking da Olimpíada")
    @app_commands.describe(limit="Número de jogadores (padrão: 10, máximo: 20)")
    async def olympiad(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra ranking da Olimpíada"""
        if not await self._check_rate_limit(interaction, "olympiad"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "olympiad")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        # Valida limite
        limit = max(1, min(20, limit))
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_olympiad_ranking()
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados da Olimpíada.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🏆 Ranking da Olimpíada",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            
            for i, player in enumerate(data[:limit], 1):
                name = player.get('char_name', 'Unknown')
                points = player.get('points', player.get('olympiad_points', 0))
                class_name = player.get('class_name', 'Unknown')
                rank = player.get('rank', i)
                
                embed.add_field(
                    name=f"#{rank} {name}",
                    value=f"**Classe:** {class_name}\n**Pontos:** {points:,}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando olympiad: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações da Olimpíada.",
                ephemeral=True
            )
    
    @app_commands.command(name="heroes", description="[PAINEL] Mostra heróis atuais da Olimpíada")
    async def heroes(self, interaction: discord.Interaction):
        """Mostra heróis atuais da Olimpíada"""
        if not await self._check_rate_limit(interaction, "heroes"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "heroes")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_olympiad_current_heroes()
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não há heróis atuais ou não foi possível obter dados.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="👑 Heróis Atuais da Olimpíada",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            
            for hero in data:
                name = hero.get('char_name', 'Unknown')
                class_name = hero.get('class_name', 'Unknown')
                hero_count = hero.get('hero_count', 0)
                hero_date = hero.get('hero_date', 'N/A')
                
                embed.add_field(
                    name=f"{name}",
                    value=f"**Classe:** {class_name}\n**Heróis:** {hero_count}\n**Data:** {hero_date}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando heroes: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações dos heróis.",
                ephemeral=True
            )
    
    # ==================== COMANDOS DE CERCOS ====================
    
    @app_commands.command(name="siege", description="[PAINEL] Mostra status dos cercos")
    async def siege(self, interaction: discord.Interaction):
        """Mostra status dos cercos"""
        if not await self._check_rate_limit(interaction, "siege"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "siege")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_siege_status()
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados dos cercos.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🏰 Status dos Cercos",
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )
            
            for siege in data:
                castle_name = siege.get('castle_name', 'Unknown')
                owner = siege.get('owner_clan', 'Nenhum')
                siege_date = self._format_time(siege.get('siege_date'))
                is_under_siege = "🟢 Em cerco" if siege.get('is_under_siege') else "⚪ Sem cerco"
                
                embed.add_field(
                    name=f"{castle_name}",
                    value=f"**Dono:** {owner}\n**Status:** {is_under_siege}\n**Próximo cerco:** {siege_date}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando siege: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações dos cercos.",
                ephemeral=True
            )
    
    @app_commands.command(name="siege-participants", description="[PAINEL] Mostra participantes de um cerco")
    @app_commands.describe(castle_id="ID do castelo (1-9)")
    async def siege_participants(self, interaction: discord.Interaction, castle_id: int):
        """Mostra participantes de um cerco"""
        if not await self._check_rate_limit(interaction, "siege_participants"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "siege_participants")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        # Valida castle_id
        if castle_id < 1 or castle_id > 9:
            await interaction.response.send_message(
                "❌ ID do castelo deve ser entre 1 e 9.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_siege_participants(castle_id)
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não há participantes ou não foi possível obter dados.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"👥 Participantes do Cerco (Castelo {castle_id})",
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )
            
            for participant in data[:15]:  # Limita a 15 para não exceder limite
                clan_name = participant.get('clan_name', 'Unknown')
                leader = participant.get('leader_name', 'Unknown')
                members = participant.get('member_count', 0)
                
                embed.add_field(
                    name=f"{clan_name}",
                    value=f"**Líder:** {leader}\n**Membros:** {members}",
                    inline=True
                )
            
            if len(data) > 15:
                embed.set_footer(text=f"Mostrando 15 de {len(data)} participantes")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando siege_participants: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar participantes do cerco.",
                ephemeral=True
            )
    
    # ==================== COMANDOS DE CLÃS E LEILÃO ====================
    
    @app_commands.command(name="clan", description="[PAINEL] Busca informações de um clã")
    @app_commands.describe(clan_name="Nome do clã")
    async def clan(self, interaction: discord.Interaction, clan_name: str):
        """Busca informações de um clã"""
        if not await self._check_rate_limit(interaction, "clan"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "clan")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        # Sanitiza input
        clan_name = self._sanitize_input(clan_name, max_length=50)
        
        if not clan_name:
            await interaction.response.send_message(
                "❌ Nome do clã inválido.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_clan_detail(clan_name)
            
            if not data:
                await interaction.followup.send(
                    f"❌ Clã '{clan_name}' não encontrado.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🏛️ {data.get('clan_name', clan_name)}",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Líder", value=data.get('leader_name', 'N/A'), inline=True)
            embed.add_field(name="Nível", value=str(data.get('level', 'N/A')), inline=True)
            embed.add_field(name="Membros", value=str(data.get('member_count', 'N/A')), inline=True)
            embed.add_field(name="Reputação", value=f"{data.get('reputation', 0):,}", inline=True)
            
            description = data.get('description')
            if description:
                embed.description = description[:500]  # Limita descrição
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando clan: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar informações do clã.",
                ephemeral=True
            )
    
    @app_commands.command(name="auction", description="[PAINEL] Mostra itens do leilão")
    @app_commands.describe(limit="Número de itens (padrão: 10, máximo: 20)")
    async def auction(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra itens do leilão"""
        if not await self._check_rate_limit(interaction, "auction"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "auction")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        # Valida limite
        limit = max(1, min(20, limit))
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_auction_items(limit)
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não há itens no leilão ou não foi possível obter dados.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="💰 Itens do Leilão",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )
            
            for item in data:
                item_name = item.get('item_name', 'Unknown')
                seller = item.get('seller', 'Unknown')
                bid = item.get('current_bid', 0)
                end_time = self._format_time(item.get('end_time'))
                
                embed.add_field(
                    name=f"{item_name}",
                    value=f"**Vendedor:** {seller}\n**Lance atual:** {bid:,} Adena\n**Termina:** {end_time}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando auction: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar itens do leilão.",
                ephemeral=True
            )
    
    @app_commands.command(name="item-search", description="[PAINEL] Busca um item")
    @app_commands.describe(item_name="Nome do item")
    async def item_search(self, interaction: discord.Interaction, item_name: str):
        """Busca um item"""
        if not await self._check_rate_limit(interaction, "item_search"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "item_search")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        # Sanitiza input
        item_name = self._sanitize_input(item_name, max_length=50)
        
        if not item_name:
            await interaction.response.send_message(
                "❌ Nome do item inválido.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.search_item(item_name)
            
            if not data or not isinstance(data, list) or len(data) == 0:
                await interaction.followup.send(
                    f"❌ Item '{item_name}' não encontrado.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"🔍 Resultados da busca: {item_name}",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            for item in data[:10]:  # Limita a 10 resultados
                item_id = item.get('item_id', 'N/A')
                name = item.get('item_name', 'Unknown')
                grade = item.get('grade', 'N/A')
                item_type = item.get('item_type', item.get('type', 'N/A'))
                
                embed.add_field(
                    name=f"{name} (ID: {item_id})",
                    value=f"**Grade:** {grade}\n**Tipo:** {item_type}",
                    inline=True
                )
            
            if len(data) > 10:
                embed.set_footer(text=f"Mostrando 10 de {len(data)} resultados")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando item_search: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar item.",
                ephemeral=True
            )
    
    # ==================== COMANDOS DE RANKING ADICIONAIS ====================
    
    @app_commands.command(name="top-rich", description="[PAINEL] Mostra ranking de riqueza (Adena)")
    @app_commands.describe(limit="Número de jogadores (padrão: 10, máximo: 20)")
    async def top_rich(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra ranking de riqueza"""
        if not await self._check_rate_limit(interaction, "top_rich"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "top_rich")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        limit = max(1, min(20, limit))
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_top_rich(limit)
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do ranking.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="💰 Top Riqueza (Adena)",
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow()
            )
            
            for i, player in enumerate(data, 1):
                name = player.get('char_name', 'Unknown')
                adena = player.get('adena', 0)
                
                embed.add_field(
                    name=f"#{i} {name}",
                    value=f"**Adena:** {adena:,}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando top_rich: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar ranking de riqueza.",
                ephemeral=True
            )
    
    @app_commands.command(name="top-online", description="[PAINEL] Mostra ranking de tempo online")
    @app_commands.describe(limit="Número de jogadores (padrão: 10, máximo: 20)")
    async def top_online(self, interaction: discord.Interaction, limit: int = 10):
        """Mostra ranking de tempo online"""
        if not await self._check_rate_limit(interaction, "top_online"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "top_online")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        limit = max(1, min(20, limit))
        
        await interaction.response.defer()
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_top_online(limit)
            
            if not data or not isinstance(data, list):
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do ranking.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="⏱️ Top Tempo Online",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            for i, player in enumerate(data, 1):
                name = player.get('char_name', 'Unknown')
                # Tenta human_onlinetime primeiro (formato humanizado), depois online_time (segundos)
                human_time = player.get('human_onlinetime')
                if human_time:
                    time_str = human_time
                else:
                    online_time = player.get('online_time', 0)
                    # Formata tempo (assumindo que está em segundos)
                    hours = online_time // 3600
                    minutes = (online_time % 3600) // 60
                    time_str = f"{hours}h {minutes}m"
                
                embed.add_field(
                    name=f"#{i} {name}",
                    value=f"**Tempo:** {time_str}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro no comando top_online: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar ranking de tempo online.",
                ephemeral=True
            )
    
    # ==================== COMANDOS AUTENTICADOS ====================
    
    @app_commands.command(name="login", description="[PAINEL] Faz login no site (requer autenticação)")
    @app_commands.describe(username="Seu nome de usuário", password="Sua senha")
    async def login(self, interaction: discord.Interaction, username: str, password: str):
        """Faz login no site"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Sanitiza inputs
            username = self._sanitize_input(username, max_length=50)
            password = password.strip()[:100]  # Limita senha mas não sanitiza muito
            
            if not username or not password:
                await interaction.followup.send(
                    "❌ Username e senha são obrigatórios.",
                    ephemeral=True
                )
                return
            
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            result = await self.auth_manager.login(
                interaction.user.id,
                username,
                password,
                domain
            )
            
            if result and result.get('success'):
                user_info = self.auth_manager.get_user_info(interaction.user.id)
                username_display = user_info.get('username', username) if user_info else username
                await interaction.followup.send(
                    f"✅ Login realizado com sucesso!\n"
                    f"Usuário: `{username_display}`\n\n"
                    f"Agora você pode usar comandos autenticados como `/account`, `/dashboard` e `/mystats`.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Credenciais inválidas. Verifique seu username e senha.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erro no comando login: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao fazer login. Tente novamente mais tarde.",
                ephemeral=True
            )
    
    @app_commands.command(name="logout", description="[PAINEL] Faz logout do site")
    async def logout(self, interaction: discord.Interaction):
        """Faz logout do site"""
        await interaction.response.defer(ephemeral=True)
        
        if not self.auth_manager.is_authenticated(interaction.user.id):
            await interaction.followup.send(
                "❌ Você não está autenticado.",
                ephemeral=True
            )
            return
        
        self.auth_manager.logout(interaction.user.id)
        await interaction.followup.send(
            "✅ Logout realizado com sucesso!",
            ephemeral=True
        )
    
    @app_commands.command(name="account", description="[PAINEL] Mostra seu perfil no site (requer login)")
    async def account(self, interaction: discord.Interaction):
        """Mostra perfil do usuário"""
        if not await self._check_rate_limit(interaction, "profile"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "profile")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        token = self.auth_manager.get_token(interaction.user.id)
        if not token:
            await interaction.followup.send(
                "❌ Você precisa fazer login primeiro. Use `/login`.",
                ephemeral=True
            )
            return
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_user_profile(token)
            
            if not data:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do perfil.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="👤 Seu Perfil",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Username", value=data.get('username', 'N/A'), inline=True)
            embed.add_field(name="Email", value=data.get('email', 'N/A'), inline=True)
            
            date_joined = data.get('date_joined')
            if date_joined:
                embed.add_field(name="Membro desde", value=self._format_time(date_joined), inline=False)
            
            last_login = data.get('last_login')
            if last_login:
                embed.add_field(name="Último login", value=self._format_time(last_login), inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro no comando profile: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar perfil.",
                ephemeral=True
            )
    
    @app_commands.command(name="dashboard", description="[PAINEL] Mostra seu dashboard (requer login)")
    async def dashboard(self, interaction: discord.Interaction):
        """Mostra dashboard do usuário"""
        if not await self._check_rate_limit(interaction, "dashboard"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "dashboard")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        token = self.auth_manager.get_token(interaction.user.id)
        if not token:
            await interaction.followup.send(
                "❌ Você precisa fazer login primeiro. Use `/login`.",
                ephemeral=True
            )
            return
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_user_dashboard(token)
            
            if not data:
                await interaction.followup.send(
                    "❌ Não foi possível obter dados do dashboard.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📊 Seu Dashboard",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            
            # Adiciona campos dinamicamente baseado nos dados retornados
            for key, value in data.items():
                if value is not None:
                    embed.add_field(
                        name=key.replace('_', ' ').title(),
                        value=str(value),
                        inline=True
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro no comando dashboard: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar dashboard.",
                ephemeral=True
            )
    
    @app_commands.command(name="mystats", description="[PAINEL] Mostra suas estatísticas (requer login)")
    async def mystats(self, interaction: discord.Interaction):
        """Mostra estatísticas do usuário"""
        if not await self._check_rate_limit(interaction, "stats"):
            reset_time = rate_limiter.get_reset_time(interaction.user.id, "stats")
            import time
            reset_seconds = int(reset_time - time.time()) if reset_time else 60
            await interaction.response.send_message(
                f"⏳ Você excedeu o limite de requisições. Tente novamente em {reset_seconds} segundos.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        token = self.auth_manager.get_token(interaction.user.id)
        if not token:
            await interaction.followup.send(
                "❌ Você precisa fazer login primeiro. Use `/login`.",
                ephemeral=True
            )
            return
        
        try:
            client, domain = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado.",
                    ephemeral=True
                )
                return
            
            data = await client.get_user_stats(token)
            
            if not data:
                await interaction.followup.send(
                    "❌ Não foi possível obter estatísticas.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📈 Suas Estatísticas",
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )
            
            # Adiciona campos dinamicamente
            for key, value in data.items():
                if value is not None:
                    embed.add_field(
                        name=key.replace('_', ' ').title(),
                        value=str(value),
                        inline=True
                    )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erro no comando stats: {e}", exc_info=True)
            await interaction.followup.send(
                "❌ Erro ao buscar estatísticas.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))

