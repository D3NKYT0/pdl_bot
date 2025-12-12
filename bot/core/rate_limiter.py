"""
Sistema de rate limiting para comandos do bot
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter por usuário e por comando"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Args:
            max_requests: Número máximo de requisições
            window_seconds: Janela de tempo em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Estrutura: {user_id: {command: [timestamps]}}
        self._requests: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    
    def is_allowed(self, user_id: int, command: str) -> bool:
        """
        Verifica se o usuário pode executar o comando
        
        Args:
            user_id: ID do usuário Discord
            command: Nome do comando
            
        Returns:
            True se permitido, False se rate limit excedido
        """
        now = time.time()
        user_requests = self._requests[user_id][command]
        
        # Remove requisições antigas (fora da janela)
        user_requests[:] = [ts for ts in user_requests if now - ts < self.window_seconds]
        
        # Verifica se excedeu o limite
        if len(user_requests) >= self.max_requests:
            return False
        
        # Adiciona a requisição atual
        user_requests.append(now)
        return True
    
    def get_remaining(self, user_id: int, command: str) -> int:
        """Retorna quantas requisições restam"""
        now = time.time()
        user_requests = self._requests[user_id][command]
        
        # Remove requisições antigas
        user_requests[:] = [ts for ts in user_requests if now - ts < self.window_seconds]
        
        return max(0, self.max_requests - len(user_requests))
    
    def get_reset_time(self, user_id: int, command: str) -> Optional[float]:
        """Retorna quando o rate limit será resetado"""
        user_requests = self._requests[user_id][command]
        if not user_requests:
            return None
        
        oldest = min(user_requests)
        return oldest + self.window_seconds
    
    def reset(self, user_id: int, command: Optional[str] = None):
        """Reseta o rate limit para um usuário/comando"""
        if command:
            self._requests[user_id][command] = []
        else:
            self._requests[user_id] = {}


# Instância global do rate limiter
# 10 requisições por minuto por usuário por comando
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

