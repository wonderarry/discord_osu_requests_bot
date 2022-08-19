from pydantic import BaseModel


class ReturnedUserData(BaseModel):
    request_type_name: str
    request_description: str
    discord_user: str
    assigned_status: str = None
    
    
class ApplicationPlayerData(BaseModel):
    player_tier_value: int
    player_profile_link: str
    player_description: str
    discord_user: str