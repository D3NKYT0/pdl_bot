"""
Cliente para comunicação com a API do site PDL
"""

import logging
import aiohttp
from typing import Optional, Dict, Any
from bot.core.config import Config

logger = logging.getLogger(__name__)


class SiteClient:
    """Cliente para fazer requisições à API do site"""
    
    def __init__(self, domain: str):
        self.domain = self._normalize_domain(domain)
        self.base_url = f"https://{self.domain}/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _normalize_domain(self, domain: str) -> str:
        """Normaliza o domínio"""
        domain = domain.strip().lower()
        if domain.startswith('http://'):
            domain = domain[7:]
        elif domain.startswith('https://'):
            domain = domain[8:]
        domain = domain.rstrip('/')
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém ou cria uma sessão HTTP"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=Config.API_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Faz uma requisição HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(Config.API_RETRY_ATTEMPTS):
            try:
                session = await self._get_session()
                async with session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"Endpoint não encontrado: {url}")
                        return None
                    else:
                        logger.warning(f"Erro HTTP {response.status} em {url}")
                        if attempt < Config.API_RETRY_ATTEMPTS - 1:
                            continue
                        return None
            except aiohttp.ClientError as e:
                logger.error(f"Erro de conexão em {url}: {e}")
                if attempt < Config.API_RETRY_ATTEMPTS - 1:
                    continue
                return None
            except Exception as e:
                logger.error(f"Erro inesperado em {url}: {e}")
                return None
        
        return None
    
    async def close(self):
        """Fecha a sessão HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    # ==================== ENDPOINTS DA API ====================
    
    async def get_server_status(self) -> Optional[Dict]:
        """Busca status do servidor"""
        return await self._request('GET', '/server/status/')
    
    async def get_players_online(self) -> Optional[Dict]:
        """Busca jogadores online"""
        return await self._request('GET', '/server/players-online/')
    
    async def get_top_pvp(self, limit: int = 10) -> Optional[Dict]:
        """Busca top PvP"""
        return await self._request('GET', f'/server/top-pvp/?limit={limit}')
    
    async def get_top_pk(self, limit: int = 10) -> Optional[Dict]:
        """Busca top PK"""
        return await self._request('GET', f'/server/top-pk/?limit={limit}')
    
    async def get_top_level(self, limit: int = 10) -> Optional[Dict]:
        """Busca top nível"""
        return await self._request('GET', f'/server/top-level/?limit={limit}')
    
    async def get_top_clan(self, limit: int = 10) -> Optional[Dict]:
        """Busca top clãs"""
        return await self._request('GET', f'/server/top-clan/?limit={limit}')
    
    async def search_character(self, name: str) -> Optional[Dict]:
        """Busca um personagem"""
        return await self._request('GET', f'/search/character/?name={name}')
    
    async def get_discord_server_info(self, discord_guild_id: str) -> Optional[Dict]:
        """Busca informações do servidor Discord no site"""
        return await self._request('GET', f'/discord/server/{discord_guild_id}/')
    
    async def check_health(self) -> bool:
        """Verifica se a API está respondendo"""
        try:
            result = await self._request('GET', '/health/')
            return result is not None
        except:
            return False
    
    # ==================== NOVOS ENDPOINTS ====================
    
    async def get_grandboss_status(self) -> Optional[Dict]:
        """Busca status dos Grand Bosses"""
        return await self._request('GET', '/server/grandboss-status/')
    
    async def get_raidboss_status(self) -> Optional[Dict]:
        """Busca status dos Raid Bosses"""
        return await self._request('GET', '/server/raidboss-status/')
    
    async def get_boss_jewel_locations(self, jewel_ids: list) -> Optional[Dict]:
        """Busca localizações dos Boss Jewels"""
        ids_str = ','.join(map(str, jewel_ids))
        return await self._request('GET', f'/server/boss-jewel-locations/?ids={ids_str}')
    
    async def get_olympiad_ranking(self) -> Optional[Dict]:
        """Busca ranking da Olimpíada"""
        return await self._request('GET', '/server/olympiad-ranking/')
    
    async def get_olympiad_heroes(self) -> Optional[Dict]:
        """Busca todos os heróis da Olimpíada"""
        return await self._request('GET', '/server/olympiad-heroes/')
    
    async def get_olympiad_current_heroes(self) -> Optional[Dict]:
        """Busca heróis atuais da Olimpíada"""
        return await self._request('GET', '/server/olympiad-current-heroes/')
    
    async def get_siege_status(self) -> Optional[Dict]:
        """Busca status dos cercos"""
        return await self._request('GET', '/server/siege/')
    
    async def get_siege_participants(self, castle_id: int) -> Optional[Dict]:
        """Busca participantes de um cerco"""
        return await self._request('GET', f'/server/siege-participants/{castle_id}/')
    
    async def get_clan_detail(self, clan_name: str) -> Optional[Dict]:
        """Busca detalhes de um clã"""
        # Sanitizar nome do clã
        clan_name = clan_name.strip().replace('/', '').replace('\\', '')
        return await self._request('GET', f'/clan/{clan_name}/')
    
    async def get_auction_items(self, limit: int = 10) -> Optional[Dict]:
        """Busca itens do leilão"""
        return await self._request('GET', f'/auction/items/?limit={limit}')
    
    async def search_item(self, name: str) -> Optional[Dict]:
        """Busca um item"""
        return await self._request('GET', f'/search/item/?name={name}')
    
    async def get_top_rich(self, limit: int = 10) -> Optional[Dict]:
        """Busca top riqueza (Adena)"""
        return await self._request('GET', f'/server/top-rich/?limit={limit}')
    
    async def get_top_online(self, limit: int = 10) -> Optional[Dict]:
        """Busca top tempo online"""
        return await self._request('GET', f'/server/top-online/?limit={limit}')
    
    # ==================== ENDPOINTS AUTENTICADOS ====================
    
    async def login(self, username: str, password: str) -> Optional[Dict]:
        """Faz login e retorna tokens JWT"""
        data = {
            'username': username,
            'password': password
        }
        return await self._request('POST', '/auth/login/', json=data)
    
    async def get_user_profile(self, token: str) -> Optional[Dict]:
        """Busca perfil do usuário (requer autenticação)"""
        headers = {'Authorization': f'Bearer {token}'}
        return await self._request('GET', '/user/profile/', headers=headers)
    
    async def get_user_dashboard(self, token: str) -> Optional[Dict]:
        """Busca dashboard do usuário (requer autenticação)"""
        headers = {'Authorization': f'Bearer {token}'}
        return await self._request('GET', '/user/dashboard/', headers=headers)
    
    async def get_user_stats(self, token: str) -> Optional[Dict]:
        """Busca estatísticas do usuário (requer autenticação)"""
        headers = {'Authorization': f'Bearer {token}'}
        return await self._request('GET', '/user/stats/', headers=headers)