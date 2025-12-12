"""
Gerenciador de autenticação JWT para comandos autenticados
Armazena tokens temporariamente e de forma segura
"""

import logging
import time
from typing import Optional, Dict
from bot.core.database import Database

logger = logging.getLogger(__name__)


class AuthManager:
    """Gerencia autenticação JWT de forma segura"""
    
    def __init__(self, db: Database):
        self.db = db
        # Cache de tokens: {user_id: {'access': token, 'refresh': token, 'expires_at': timestamp}}
        self._token_cache: Dict[int, Dict] = {}
        # Tokens expiram em 1 hora (padrão JWT)
        self._token_ttl = 3600
    
    async def login(self, user_id: int, username: str, password: str, site_domain: str) -> Optional[Dict]:
        """
        Faz login e armazena token temporariamente
        
        Args:
            user_id: ID do usuário Discord
            username: Nome de usuário do site
            password: Senha (será descartada após login)
            site_domain: Domínio do site
            
        Returns:
            Dict com tokens ou None se falhar
        """
        try:
            from bot.core.site_client import SiteClient
            
            client = SiteClient(site_domain)
            result = await client.login(username, password)
            await client.close()
            
            if not result or 'access' not in result:
                return None
            
            # Armazena token no cache (não no banco de dados por segurança)
            expires_at = time.time() + self._token_ttl
            self._token_cache[user_id] = {
                'access': result['access'],
                'refresh': result.get('refresh'),
                'expires_at': expires_at,
                'username': username,
                'site_domain': site_domain
            }
            
            logger.info(f"Login bem-sucedido para usuário {user_id} ({username})")
            return {'success': True, 'username': username}
            
        except Exception as e:
            logger.error(f"Erro ao fazer login: {e}", exc_info=True)
            return None
    
    def get_token(self, user_id: int) -> Optional[str]:
        """
        Obtém o token de acesso do usuário
        
        Args:
            user_id: ID do usuário Discord
            
        Returns:
            Token de acesso ou None se não autenticado/expirado
        """
        if user_id not in self._token_cache:
            return None
        
        token_data = self._token_cache[user_id]
        
        # Verifica se expirou
        if time.time() >= token_data['expires_at']:
            del self._token_cache[user_id]
            return None
        
        return token_data['access']
    
    def is_authenticated(self, user_id: int) -> bool:
        """Verifica se o usuário está autenticado"""
        token = self.get_token(user_id)
        return token is not None
    
    def logout(self, user_id: int):
        """Remove autenticação do usuário"""
        if user_id in self._token_cache:
            del self._token_cache[user_id]
            logger.info(f"Logout do usuário {user_id}")
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Obtém informações do usuário autenticado"""
        if user_id not in self._token_cache:
            return None
        
        token_data = self._token_cache[user_id]
        
        # Verifica se expirou
        if time.time() >= token_data['expires_at']:
            del self._token_cache[user_id]
            return None
        
        return {
            'username': token_data.get('username'),
            'site_domain': token_data.get('site_domain')
        }

