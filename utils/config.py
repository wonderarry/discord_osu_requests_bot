from pydantic import BaseSettings
from .logging_setup import retrieve_logger
from oauth2client.service_account import ServiceAccountCredentials
import gspread_asyncio

class Settings(BaseSettings):
        
    app_id: str
    guild_id: str
    pub_key: str
    bot_token: str
    creds_filename: str
    requests_sheet_id: str
    looking_for_team_channel_id: int
    osu_api_key: str
    #high ranks mean lower rank number (higher pp value)
    #--------high tiers--------#
    high_rank_high_tier_limit: int
    low_rank_high_tier_limit: int
    #--------mid tiers--------#
    high_rank_mid_tier_limit: int
    low_rank_mid_tier_limit: int
    #--------low tiers--------#
    high_rank_low_tier_limit: int
    low_rank_low_tier_limit: int
    
    class Config:
        env_file = '.env'
        
settings = Settings()

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

google_client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: ServiceAccountCredentials.from_json_keyfile_name(settings.creds_filename, scopes=scope))

retrieve_logger(__name__).debug("Successfully obtained settings!")