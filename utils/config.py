from pydantic import BaseSettings
from .logging_setup import retrieve_logger

class Settings(BaseSettings):
        
    app_id: str
    guild_id: str
    pub_key: str
    bot_token: str
    
    class Config:
        env_file = '.env'
        

settings = Settings()
retrieve_logger(__name__).debug("Successfully obtained settings!")