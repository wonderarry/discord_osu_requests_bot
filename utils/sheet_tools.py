from utils.config import settings, google_client_manager
from typing import Any, List, Optional, Union
from discord import Interaction
import aiohttp
import json

async def get_requests_worksheet():
    session = await google_client_manager.authorize()
    ss = await session.open_by_key(settings.requests_sheet_id)
    ws = await ss.get_worksheet(settings.requests_worksheet)
    
    return ws




async def generate_request_lookup_string(worksheet) -> str:
    last_empty_row_index = len(await worksheet.col_values(1)) + 1
    lookup_string = 'A' + str(last_empty_row_index) + ':D' + str(last_empty_row_index)
    
    return lookup_string


async def validate_osu_profile(provided_tier: int, provided_id: int, badge_count: int) -> List[Union[int, Optional[str]]]:
    def create_link_from_id(id):
        return 'https://osu.ppy.sh/users/' + str(id)
    
    async def get_osu_rank_from_id(id: int) -> Optional[int]:
        api_link = f'https://osu.ppy.sh/api/get_user?u={id}&k={settings.osu_api_key}'
        async with aiohttp.ClientSession() as session:
            async with session.get(api_link) as response:
                result = await response.json()
                if len(result) == 0:
                    return None
                return int(result[0]['pp_rank'])   
    
    def validate_osu_rank(tier, rank):
        if tier == 0: #high tier
            if rank < settings.high_rank_high_tier_limit or rank > settings.low_rank_high_tier_limit:
                return False
        elif tier == 1: #mid tier
            if rank < settings.high_rank_mid_tier_limit or rank > settings.low_rank_mid_tier_limit:
                return False
        elif tier == 2: #low tier
            if rank < settings.high_rank_low_tier_limit or rank > settings.low_rank_low_tier_limit:
                return False
        return True
    
    def is_profile_exists(rank):
        if rank is None:
            return False
        return True
    
    rank = await get_osu_rank_from_id(provided_id)
    if not is_profile_exists(rank):
        return (False, "The player's profile is restricted or does not exist!", None, None, None)
    
    bws_rank = max(1, rank ** (settings.bws_factor ** (badge_count ** 2)))
    
    if not validate_osu_rank(provided_tier, bws_rank):
        return (False, "The player's rank is outside the tier boundaries", None, rank, bws_rank)
    
    return (True, None, create_link_from_id(provided_id), rank, bws_rank)


def get_discord_name(interaction: Interaction) -> str:
    return interaction.user.name + '#' + interaction.user.discriminator

def prepare_player_description(osu_profile: str, tournament_tier_name: str, text_description: str, rank: int, badges: int, bws_rank: float) -> str:
    result = f'Player tier: {tournament_tier_name}\nosu! profile: {osu_profile}\nStrengths and weaknesses: {text_description}\nosu! rank: {rank}\nBadge count: {badges}\nBWS rank: {bws_rank}'
    return result

def prepare_request_description(discord_username: str, request_type_name: str, text_description: str) -> str:
    result = f'Username: {discord_username}\nRequest type: {request_type_name}\nTextual description: {text_description}'
    return result

async def get_application_worksheet():
    session = await google_client_manager.authorize()
    ss = await session.open_by_key(settings.application_sheet_id)
    ws = await ss.get_worksheet(settings.application_worksheet)
    
    return ws

async def generate_application_lookup_string(worksheet) -> str:
    last_empty_row_index = len(await worksheet.col_values(1)) + 1
    lookup_string = 'A' + str(last_empty_row_index) + ':G' + str(last_empty_row_index)
    
    return lookup_string