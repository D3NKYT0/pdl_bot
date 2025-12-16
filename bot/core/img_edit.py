"""
Módulo para edição de imagens - adaptado do projeto Ashley
"""

import re
import unicodedata
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps, UnidentifiedImageError


def remove_acentos_e_caracteres_especiais(word):
    """Remove acentos e caracteres especiais de uma string"""
    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', word)
    palavra_sem_acento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z \\\]', '', palavra_sem_acento)


async def get_avatar(display_avatar_url: str, x: int = -1, y: int = -1, rect: bool = False):
    """
    Baixa e processa avatar do Discord
    
    Args:
        display_avatar_url: URL do avatar do Discord
        x: Largura desejada (-1 para manter original)
        y: Altura desejada (-1 para manter original)
        rect: Se True, mantém formato retangular; se False, faz círculo
    
    Returns:
        PIL Image com o avatar processado
    """
    # URL padrão caso o avatar não seja válido
    default_avatar = "https://cdn.discordapp.com/embed/avatars/0.png"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(display_avatar_url) as response:
                if response.status == 200:
                    avatar_bytes = await response.read()
                    avatar = Image.open(BytesIO(avatar_bytes)).convert('RGBA')
                else:
                    # Se falhar, tenta o avatar padrão
                    async with session.get(default_avatar) as response:
                        avatar_bytes = await response.read()
                        avatar = Image.open(BytesIO(avatar_bytes)).convert('RGBA')
    except (aiohttp.ClientError, UnidentifiedImageError, Exception):
        # Em caso de erro, usa avatar padrão
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(default_avatar) as response:
                    avatar_bytes = await response.read()
                    avatar = Image.open(BytesIO(avatar_bytes)).convert('RGBA')
        except Exception:
            # Se tudo falhar, cria uma imagem padrão
            avatar = Image.new('RGBA', (111, 135), (128, 128, 128, 255))

    # Redimensiona se necessário
    if x >= 0 and y >= 0:
        avatar = avatar.resize((x, y), Image.Resampling.LANCZOS)

    # Se não for retangular, faz círculo
    if not rect:
        big_avatar = (avatar.size[0] * 3, avatar.size[1] * 3)
        mascara = Image.new('L', big_avatar, 0)
        trim = ImageDraw.Draw(mascara)
        trim.ellipse((0, 0) + big_avatar, fill=255)
        mascara = mascara.resize(avatar.size, Image.Resampling.LANCZOS)
        avatar.putalpha(mascara)
        exit_avatar = ImageOps.fit(avatar, mascara.size, centering=(0.5, 0.5))
        exit_avatar.putalpha(mascara)
        avatar = exit_avatar

    return avatar
