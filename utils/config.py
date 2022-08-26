from pydantic import BaseSettings
from .logging_setup import retrieve_logger
from oauth2client.service_account import ServiceAccountCredentials
import gspread_asyncio


class DiscordCreds(BaseSettings):
    app_id: str
    guild_id: str
    pub_key: str
    bot_token: str

    class Config:
        env_file = '.env'


class ServiceCreds(DiscordCreds):
    # google credentials
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str


class OsuBotManager(ServiceCreds):
    osu_api_key: str
    # high ranks mean lower rank number (higher pp value)
    #--------high tiers--------#
    high_rank_high_tier_limit: int
    low_rank_high_tier_limit: int
    #--------mid tiers--------#
    high_rank_mid_tier_limit: int
    low_rank_mid_tier_limit: int
    #--------low tiers--------#
    high_rank_low_tier_limit: int
    low_rank_low_tier_limit: int
    bws_factor: float


class Settings(OsuBotManager):

    requests_sheet_id: str
    requests_worksheet: int

    application_sheet_id: str
    application_worksheet: int

    looking_for_team_channel_id: int


settings = Settings()

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

#google_client_manager = gspread_asyncio.AsyncioGspreadClientManager(
    #lambda: ServiceAccountCredentials.from_json_keyfile_name(settings.creds_filename, scopes=scope))

retrieve_logger(__name__).debug("Successfully obtained settings!")

creds_data = settings.dict(include={
    'type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id',
    'auth_uri', 'token_uri', 'auth_provider_x509_cert_url', 'client_x509_cert_url'})
creds_data['private_key'] = creds_data['private_key'].replace('\\n', '\n')

google_client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: ServiceAccountCredentials.from_json_keyfile_dict(creds_data))


