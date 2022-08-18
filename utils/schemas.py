from pydantic import BaseModel


class ReturnedUserData(BaseModel):
    request_type_name: str
    request_description: str
    discord_user: str
    assigned_status: str = None
    