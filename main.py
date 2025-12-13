"""
Bot Discord para integração com instâncias do PDL
Bot global que se conecta a qualquer instância do site via API
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import discord
from discord.ext import commands
from bot.core.config import Config
from bot.core.database import Database
from bot.core.site_client import SiteClient

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
log_file = os.getenv('LOG_FILE', 'bot.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class PDLBot(commands.Bot):
    """Bot principal do PDL"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None,  # Vamos criar um custom
            case_insensitive=True
        )
        
        self.config = Config()
        self.db = Database()
        self.site_clients = {}  # Cache de clientes por domínio
        
    async def setup_hook(self):
        """Configuração inicial do bot"""
        logger.info("Configurando bot...")
        
        # Conectar ao MongoDB
        await self.db.connect()
        logger.info("Conectado ao MongoDB")
        
        # Carregar cogs
        try:
            # Cogs principais
            await self.load_extension('bot.cogs.server_detection')
            await self.load_extension('bot.cogs.server_info')
            await self.load_extension('bot.cogs.player_commands')
            await self.load_extension('bot.cogs.help')
            
            # Fase 1 - Essenciais
            await self.load_extension('bot.cogs.feedback')
            await self.load_extension('bot.cogs.server_config')
            
            # Fase 2 - Importantes
            await self.load_extension('bot.cogs.logging_system')
            await self.load_extension('bot.cogs.announcements')
            await self.load_extension('bot.cogs.notifications')
            
            # Fase 3 - Melhorias
            await self.load_extension('bot.cogs.user_profile')
            
            # Fase 4 - Extras
            await self.load_extension('bot.cogs.utility')
            await self.load_extension('bot.cogs.vote')
            
        except Exception as e:
            logger.error(f"Erro ao carregar cogs: {e}", exc_info=True)
        
        logger.info("Cogs carregados")
        
    async def on_ready(self):
        """Evento quando o bot está pronto"""
        logger.info(f'Bot conectado como {self.user}')
        logger.info(f'ID: {self.user.id}')
        logger.info(f'Conectado em {len(self.guilds)} servidores')
        
        # Sincronizar comandos slash
        try:
            synced = await self.tree.sync()
            logger.info(f'Sincronizados {len(synced)} comandos slash')
        except Exception as e:
            logger.error(f'Erro ao sincronizar comandos: {e}')
        
        # Verificar servidores cadastrados
        await self.check_registered_servers()
        
    async def check_registered_servers(self):
        """Verifica quais servidores estão cadastrados"""
        logger.info("Verificando servidores cadastrados...")
        
        for guild in self.guilds:
            guild_id = str(guild.id)
            server_data = await self.db.get_server_by_discord_id(guild_id)
            
            if server_data:
                logger.info(f"Servidor {guild.name} ({guild_id}) está cadastrado: {server_data['site_domain']}")
            else:
                logger.debug(f"Servidor {guild.name} ({guild_id}) não está cadastrado")
    
    async def get_site_client(self, domain: str) -> SiteClient:
        """Obtém ou cria um cliente para um domínio específico"""
        if domain not in self.site_clients:
            self.site_clients[domain] = SiteClient(domain)
        
        return self.site_clients[domain]
    
    async def on_guild_join(self, guild: discord.Guild):
        """Evento quando o bot entra em um servidor"""
        logger.info(f"Bot entrou no servidor: {guild.name} (ID: {guild.id})")
        
        # Verificar se o servidor está cadastrado
        server_data = await self.db.get_server_by_discord_id(str(guild.id))
        
        if server_data:
            logger.info(f"Servidor {guild.name} está cadastrado: {server_data['site_domain']}")
        else:
            logger.info(f"Servidor {guild.name} não está cadastrado. Use /register para cadastrar.")
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Evento quando o bot sai de um servidor"""
        logger.info(f"Bot saiu do servidor: {guild.name} (ID: {guild.id})")
    
    async def close(self):
        """Fechar conexões ao desligar"""
        await self.db.close()
        await super().close()


async def main():
    """Função principal"""
    bot = PDLBot()
    
    try:
        await bot.start(Config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Desligando bot...")
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {e}", exc_info=True)
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
