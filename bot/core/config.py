"""
Configurações do bot
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configurações do bot"""
    
    # Discord
    TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
    PREFIX = os.getenv('DISCORD_BOT_PREFIX', '!')
    
    # MongoDB
    # Default uses Docker service name. Override with MONGODB_URI env var for local development
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://mongodb:27017')
    MONGODB_DB = os.getenv('MONGODB_DB', 'pdl_bot')
    
    # API
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
    
    # Cache
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutos
    
    @classmethod
    def validate(cls):
        """Valida se todas as configurações necessárias estão presentes"""
        if not cls.TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN não configurado")
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI não configurado")
        
        return True
