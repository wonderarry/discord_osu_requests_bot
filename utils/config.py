from pydantic import BaseSettings
from .logging_setup import retrieve_logger
from oauth2client.service_account import ServiceAccountCredentials
class Settings(BaseSettings):
        
    app_id: str
    guild_id: str
    pub_key: str
    bot_token: str
    creds_filename: str
    sheet_id: str
    
    class Config:
        env_file = '.env'
        
settings = Settings()

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]



retrieve_logger(__name__).debug("Successfully obtained settings!")