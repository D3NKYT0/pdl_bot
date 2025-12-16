"""
Cog para comando de rank - gera imagem similar ao Ashley Bot
"""

import logging
import re
import unicodedata
from random import choice
from pathlib import Path
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from bot.core.img_edit import get_avatar, remove_acentos_e_caracteres_especiais

logger = logging.getLogger(__name__)

# Caminho base dos assets
BASE_PATH = Path(__file__).parent.parent.parent


class Rank(commands.Cog):
    """Comando para exibir rank do personagem com imagem"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def _get_site_client(self, guild_id: int):
        """Obtém o cliente do site para o servidor"""
        server_data = await self.db.get_server_by_discord_id(str(guild_id))
        
        if not server_data:
            return None
        
        return await self.bot.get_site_client(server_data['site_domain'])
    
    async def _get_character_ranking_position(self, client, character_name: str):
        """
        Obtém a posição do personagem no ranking de nível
        Tenta usar endpoint específico, senão calcula manualmente
        """
        # Primeiro tenta endpoint específico
        try:
            result = await client.get_character_ranking_position(character_name, 'level')
            if result and result.get('position'):
                return result.get('position')
        except Exception as e:
            logger.debug(f"Endpoint de ranking não disponível: {e}")
        
        # Se não tiver endpoint, calcula manualmente buscando o top
        try:
            top_data = await client.get_top_level(500)  # Busca muitos para encontrar
            if isinstance(top_data, list):
                for idx, player in enumerate(top_data, 1):
                    if player.get('char_name', '').lower() == character_name.lower():
                        return idx
            elif isinstance(top_data, dict) and 'results' in top_data:
                for idx, player in enumerate(top_data['results'], 1):
                    if player.get('char_name', '').lower() == character_name.lower():
                        return idx
        except Exception as e:
            logger.debug(f"Erro ao calcular posição manualmente: {e}")
        
        return None
    
    def _text_align(self, box, text, font_t, draw):
        """Alinha texto no centro de uma caixa"""
        x1, y1, x2, y2 = box
        # Usar textbbox ao invés de textsize (deprecated)
        bbox = draw.textbbox((0, 0), text.upper(), font=font_t)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (x2 - x1 - w) // 2 + x1
        y = (y2 - y1 - h) // 2 + y1
        return x, y
    
    async def _generate_rank_image(self, member: discord.Member, character_data: dict, 
                                   user_game_data: dict = None, position: int = None):
        """
        Gera a imagem de rank
        
        Args:
            member: Membro do Discord
            character_data: Dados do personagem do Django
            user_game_data: Dados de XP, conquistas e jogos do usuário
            position: Posição no ranking (opcional)
        """
        # Backgrounds disponíveis
        background = {
            "01": "background_1",
            "02": "background_2",
            "03": "background_3",
            "04": "background_4",
            "05": "background_5",
            "06": "background_6",
            "07": "background_7",
            "08": "background_8",
            "09": "background_9",
            "10": "staffer",
            "11": "vip",
        }
        
        # Escolhe background aleatório (pode ser customizado depois)
        key_bg = choice(["01", "02", "03", "04", "05", "06", "07", "08", "09"])
        
        # Verifica se é VIP ou staff (pode ser implementado depois)
        # if character_data.get('vip', False):
        #     key_bg = "11"
        # if member.id in self.bot.team:  # Se tiver lista de staff
        #     key_bg = "10"
        
        # Carrega background
        bg_path = BASE_PATH / "images" / "rank" / "background" / f"{background[key_bg]}.png"
        if not bg_path.exists():
            logger.error(f"Background não encontrado: {bg_path}")
            # Tenta usar background padrão
            bg_path = BASE_PATH / "images" / "rank" / "background" / "background_1.png"
            if not bg_path.exists():
                logger.error("Nenhum background disponível")
                return None
        
        image = Image.open(bg_path).convert('RGBA')
        draw = ImageDraw.Draw(image)
        
        # Usa level do sistema PDL se disponível, senão usa do personagem
        if user_game_data:
            level = user_game_data.get('level', 0)
            # Estrelas baseadas na quantidade de conquistas (máximo 25)
            achievements_count = user_game_data.get('achievements_count', 0)
            star = min(achievements_count, 25)
        else:
            # Fallback para dados do personagem
            level = character_data.get('level', 0)
            star = min(level // 3, 25)  # Máximo 25 estrelas
        
        # Carrega overlay de estrelas
        star_path = BASE_PATH / "images" / "rank" / "star" / f"star_{star}.png"
        if star_path.exists():
            stars_dashboard = Image.open(star_path).convert('RGBA')
            image.paste(stars_dashboard, (0, 0), stars_dashboard)
        
        # Retângulos para posicionar elementos
        rectangles = {
            "avatar": [9, 8, 119, 142],
            "patent": [149, 59, 239, 145],
            "num": [220, 126, 238, 144],
            "top": [327, 64, 388, 93],
            "title": [263, 113, 390, 142],
            "name": [0, 160, 399, 191],
        }
        
        # Adiciona avatar
        avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url
        avatar = await get_avatar(avatar_url, 111, 135, True)
        image.paste(avatar, (rectangles["avatar"][0], rectangles["avatar"][1]), avatar)
        
        # Adiciona patente (baseado no nível do sistema PDL)
        if user_game_data:
            # Usa o método get_patent_level se disponível, senão calcula
            patent = user_game_data.get('level', 1)
            patent = min(max(1, patent), 30)  # Limita a 30
        else:
            patent = min(max(1, level // 5), 30)  # Patente de 1 a 30 baseado no nível
        patent_path = BASE_PATH / "images" / "patente" / f"{patent}.png"
        if patent_path.exists():
            try:
                patent_img = Image.open(patent_path).convert('RGBA')
                patent_img = patent_img.resize((80, 80), Image.Resampling.LANCZOS)
                image.paste(patent_img, (rectangles["patent"][0] + 5, rectangles["patent"][1] - 10), patent_img)
            except Exception as e:
                logger.warning(f"Erro ao carregar patente: {e}")
        
        # Número da patente
        try:
            font_small = ImageFont.truetype(str(BASE_PATH / "fonts" / "bot.otf"), 12)
            x_, y_ = self._text_align(rectangles["num"], str(patent), font_small, draw)
            draw.text(xy=(x_, y_), text=str(patent).upper(), fill=(255, 255, 255), font=font_small)
        except Exception as e:
            logger.warning(f"Erro ao carregar fonte pequena: {e}")
        
        # Posição no ranking
        try:
            font_position = ImageFont.truetype(str(BASE_PATH / "fonts" / "bot.otf"), 28)
            position_text = str(position) if position else "?"
            x_, y_ = self._text_align(rectangles["top"], position_text, font_position, draw)
            draw.text(xy=(x_, y_), text=position_text.upper(), fill=(0, 0, 0), font=font_position)
        except Exception as e:
            logger.warning(f"Erro ao desenhar posição: {e}")
        
        # Título (PLAYER ou STAFF)
        try:
            font_title = ImageFont.truetype(str(BASE_PATH / "fonts" / "bot.otf"), 28)
            title = "STAFF" if member.guild_permissions.administrator else "PLAYER"
            x_, y_ = self._text_align(rectangles["title"], title, font_title, draw)
            draw.text(xy=(x_, y_), text=title.upper(), fill=(0, 0, 0), font=font_title)
        except Exception as e:
            logger.warning(f"Erro ao desenhar título: {e}")
        
        # Nome do usuário
        try:
            font_name = ImageFont.truetype(str(BASE_PATH / "fonts" / "bot.otf"), 38)
            nome = remove_acentos_e_caracteres_especiais(str(member))
            x_, y_ = self._text_align(rectangles["name"], nome, font_name, draw)
            # Sombra
            draw.text(xy=(x_ + 1, y_ + 1), text=nome.upper(), fill=(0, 0, 0), font=font_name)
            # Texto principal
            draw.text(xy=(x_, y_), text=nome.upper(), fill=(255, 255, 255), font=font_name)
        except Exception as e:
            logger.warning(f"Erro ao desenhar nome: {e}")
        
        # Salva imagem temporária
        output_path = BASE_PATH / "rank_temp.png"
        image.save(output_path)
        
        return output_path
    
    @app_commands.command(name="rank", description="[PAINEL] Mostra seu rank com imagem personalizada")
    @app_commands.describe(character_name="Nome do personagem no jogo (deixe vazio para buscar pelo Discord)")
    async def rank(self, interaction: discord.Interaction, character_name: str = None):
        """Gera imagem de rank do personagem"""
        await interaction.response.defer()
        
        try:
            client = await self._get_site_client(interaction.guild.id)
            
            if not client:
                await interaction.followup.send(
                    "❌ Este servidor não está registrado. Use `/register <domínio>` para registrar.",
                    ephemeral=True
                )
                return
            
            # Se não forneceu nome, tenta buscar pelo Discord ID
            if not character_name:
                # Aqui você pode implementar uma busca por Discord ID se tiver essa funcionalidade
                await interaction.followup.send(
                    "❌ Por favor, forneça o nome do personagem: `/rank <nome_do_personagem>`",
                    ephemeral=True
                )
                return
            
            # Busca dados do personagem
            character_data_list = await client.search_character(character_name)
            
            if not character_data_list or len(character_data_list) == 0:
                await interaction.followup.send(
                    f"❌ Personagem `{character_name}` não encontrado.",
                    ephemeral=True
                )
                return
            
            # Pega o primeiro resultado
            character_data = character_data_list[0] if isinstance(character_data_list, list) else character_data_list
            
            # Busca dados de XP e conquistas do usuário (tenta pelo nome do personagem como username)
            user_game_data = None
            try:
                # Tenta buscar dados do usuário pelo nome do personagem
                user_game_data = await client.get_user_game_data(character_name)
            except Exception as e:
                logger.debug(f"Erro ao buscar dados do usuário: {e}")
            
            # Busca posição no ranking
            position = await self._get_character_ranking_position(client, character_name)
            
            # Gera imagem
            image_path = await self._generate_rank_image(
                interaction.user,
                character_data,
                user_game_data,
                position
            )
            
            if not image_path or not image_path.exists():
                await interaction.followup.send(
                    "❌ Erro ao gerar imagem de rank.",
                    ephemeral=True
                )
                return
            
            # Envia imagem
            file = discord.File(str(image_path), filename="rank.png")
            await interaction.followup.send(file=file)
            
            # Remove arquivo temporário
            try:
                image_path.unlink()
            except:
                pass
            
        except Exception as e:
            logger.error(f"Erro no comando rank: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Erro ao gerar rank: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Rank(bot))
