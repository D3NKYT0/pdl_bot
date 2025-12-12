"""
Gerenciamento do banco de dados MongoDB
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bot.core.config import Config

logger = logging.getLogger(__name__)


class Database:
    """Classe para gerenciar conexão e operações no MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
    async def connect(self):
        """Conecta ao MongoDB"""
        try:
            self.client = AsyncIOMotorClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DB]
            
            # Testar conexão
            await self.client.admin.command('ping')
            logger.info("Conectado ao MongoDB")
            
            # Criar índices
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Cria índices necessários"""
        try:
            # Índice único para discord_guild_id
            await self.db.servers.create_index("discord_guild_id", unique=True)
            
            # Índice para site_domain
            await self.db.servers.create_index("site_domain")
            
            logger.info("Índices criados")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
    
    async def close(self):
        """Fecha a conexão"""
        if self.client:
            self.client.close()
            logger.info("Conexão MongoDB fechada")
    
    # ==================== SERVIDORES ====================
    
    async def register_server(self, discord_guild_id: str, site_domain: str, 
                             server_name: str = None) -> Dict:
        """Registra um servidor Discord com um domínio do site"""
        try:
            # Normalizar domínio (remover http/https, barras finais)
            site_domain = self._normalize_domain(site_domain)
            
            # Dados para atualizar (sem created_at para evitar conflito)
            server_data = {
                "discord_guild_id": discord_guild_id,
                "site_domain": site_domain,
                "server_name": server_name,
                "is_active": True,
            }
            
            # Usar $setOnInsert apenas para created_at (só define na inserção)
            result = await self.db.servers.update_one(
                {"discord_guild_id": discord_guild_id},
                {
                    "$set": server_data,
                    "$setOnInsert": {"created_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            logger.info(f"Servidor registrado: {discord_guild_id} -> {site_domain}")
            
            # Buscar documento atualizado para retornar dados completos
            updated_server = await self.db.servers.find_one({"discord_guild_id": discord_guild_id})
            return updated_server or server_data
            
        except Exception as e:
            logger.error(f"Erro ao registrar servidor: {e}")
            raise
    
    async def get_server_by_discord_id(self, discord_guild_id: str) -> Optional[Dict]:
        """Busca servidor pelo ID do Discord"""
        try:
            server = await self.db.servers.find_one({"discord_guild_id": discord_guild_id})
            return server
        except Exception as e:
            logger.error(f"Erro ao buscar servidor: {e}")
            return None
    
    async def get_server_by_domain(self, site_domain: str) -> Optional[Dict]:
        """Busca servidor pelo domínio do site"""
        try:
            site_domain = self._normalize_domain(site_domain)
            server = await self.db.servers.find_one({"site_domain": site_domain})
            return server
        except Exception as e:
            logger.error(f"Erro ao buscar servidor por domínio: {e}")
            return None
    
    async def unregister_server(self, discord_guild_id: str) -> bool:
        """Remove registro de um servidor"""
        try:
            result = await self.db.servers.delete_one({"discord_guild_id": discord_guild_id})
            logger.info(f"Servidor removido: {discord_guild_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao remover servidor: {e}")
            return False
    
    async def list_servers(self) -> List[Dict]:
        """Lista todos os servidores registrados"""
        try:
            servers = await self.db.servers.find({"is_active": True}).to_list(length=None)
            return servers
        except Exception as e:
            logger.error(f"Erro ao listar servidores: {e}")
            return []
    
    async def update_server_status(self, discord_guild_id: str, is_active: bool):
        """Atualiza status de um servidor"""
        try:
            await self.db.servers.update_one(
                {"discord_guild_id": discord_guild_id},
                {"$set": {"is_active": is_active}}
            )
            logger.info(f"Status atualizado: {discord_guild_id} -> {is_active}")
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
    
    # ==================== CACHE ====================
    
    async def cache_set(self, key: str, value: Dict, ttl: int = None):
        """Armazena dados em cache"""
        try:
            ttl = ttl or Config.CACHE_TTL
            cache_data = {
                "key": key,
                "value": value,
                "expires_at": None  # MongoDB TTL index cuidará disso
            }
            await self.db.cache.update_one(
                {"key": key},
                {"$set": cache_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Erro ao armazenar cache: {e}")
    
    async def cache_get(self, key: str) -> Optional[Dict]:
        """Recupera dados do cache"""
        try:
            cached = await self.db.cache.find_one({"key": key})
            if cached:
                return cached.get("value")
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar cache: {e}")
            return None
    
    # ==================== UTILS ====================
    
    def _normalize_domain(self, domain: str) -> str:
        """Normaliza um domínio (remove protocolo, barras, etc)"""
        domain = domain.strip().lower()
        
        # Remover protocolo
        if domain.startswith('http://'):
            domain = domain[7:]
        elif domain.startswith('https://'):
            domain = domain[8:]
        
        # Remover barras finais
        domain = domain.rstrip('/')
        
        # Remover www (opcional)
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
