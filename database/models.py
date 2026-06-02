
from typing import Generic, NotRequired, Optional, TypeVar, TypedDict
from datetime import datetime

T = TypeVar("T")

class SimpleResponse(TypedDict):
    success: bool
    error: Optional[str]

class ReturningResponse(TypedDict, Generic[T]):
    success: bool
    data: Optional[T]
    error: Optional[str]

class TeamMember(TypedDict):
    id: int
    nama: str
    rank: str
    jabatan: str
    user_id: Optional[int]
    last_login: datetime
    team_id: int

class Team(TypedDict):
    team_id: int
    name: str
    created_at: datetime
    created_by: int

class TeamResponse(TypedDict):
    success: bool
    team_data: Optional[dict[int, Team]]
    team_member_data: Optional[dict[str, TeamMember]]
    error: Optional[str]

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
    player_log_channel_id: int | None

class BountySettings(TypedDict):
    bounty_log_channel_id: int | None
    alert_channel_id: int | None

class GeneralSettings(TypedDict):
    player_list_channel_id: int | None

class GuildSettings(TypedDict):
    auction: NotRequired[AuctionSettings]
    team: NotRequired[TeamSettings]
    bounty: NotRequired[BountySettings]
    general: NotRequired[GeneralSettings]

class LoadSettingsResponse(TypedDict):
    success: bool
    data: dict[int, GuildSettings] | None
    error: str | None
    
class PlayerLogEntry(TypedDict):
    nickname: str
    online_at: datetime