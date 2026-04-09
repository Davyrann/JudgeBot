
from typing import NotRequired, TypedDict
from datetime import datetime

class TabelAuction(TypedDict):
    id: int
    guild_id: int
    user_id: int
    item_name: str
    is_active: bool
    created_at: datetime
    is_permanent: bool

class ItemListAuction(TypedDict):
    guild_id: int
    item_name: str
    error: str | None

class AuctionSingleResponse(TypedDict):
    success: bool
    data: TabelAuction | None
    error: str | None

class AuctionListResponse(TypedDict):
    success: bool
    data: list[TabelAuction] | list[ItemListAuction] | None
    error: str | None

class ItemUser(TypedDict):
    user_id: int
    auction_id: int
    
class ItemUserResponse(TypedDict):
    success: bool
    data: list[ItemUser] | None
    error: str | None

class SetSettingsResponse(TypedDict):
    success: bool
    error: str | None

class AuctionSettings(TypedDict):
    event_channel_id: int | None
    alert_channel_id: int | None

class TeamSettings(TypedDict):
    team_log_channel_id: int | None 
    member_join_alert_id: int | None

class BountySettings(TypedDict):
    bounty_log_channel_id: int | None
    alert_channel_id: int | None

class GuildSettings(TypedDict):
    auction: NotRequired[AuctionSettings]
    team: NotRequired[TeamSettings]
    bounty: NotRequired[BountySettings]

class LoadSettingsResponse(TypedDict):
    success: bool
    data: dict[int, GuildSettings] | None
    error: str | None