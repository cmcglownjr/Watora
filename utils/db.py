import dataclasses
import asyncio
import motor.motor_asyncio
from typing import Any, Dict, Final, Optional
from abc import ABC

class Settings(ABC):
    id: int

class GuildSettings(Settings):
    prefix: str = dataclasses.field(default=globprefix)
    language: str = dataclasses.field(default="english")
    volume: float = dataclasses.field(default=def_v)
    vote: int = dataclasses.field(default=def_vote)
    timer: int = dataclasses.field(default=def_time)
    autoplay: bool = dataclasses.field(default=True)
    owo: bool = dataclasses.field(default=False)
    lazy: bool = dataclasses.field(default=False)
    channel: Optional[int] = dataclasses.field(default=None)
    bound: Optional[int] = dataclasses.field(default=None)
    customcommands: Dict[str, str] = dataclasses.field(default_factory=dict)
    points: Dict[str, int] = dataclasses.field(default_factory=dict)
    welcomes: Dict[str, str] = dataclasses.field(default_factory=dict)
    goodbyes: Dict[str, str] = dataclasses.field(default_factory=dict)
    autosongs: Dict[str, str] = dataclasses.field(default_factory=dict)
    djs: list = dataclasses.field(default_factory=list)
    roles: list = dataclasses.field(default_factory=list)
    autoroles: list = dataclasses.field(default_factory=list)
    disabledchannels: Dict[str, bool] = dataclasses.field(default_factory=dict)
    disabledcommands: list = dataclasses.field(default_factory=list)
    blacklisted: list = dataclasses.field(default_factory=list)
    clans: list = dataclasses.field(default_factory=list)
    respect: int = dataclasses.field(default=0)

class GlobSettings(Settings):
    blacklisted: list = dataclasses.field(default_factory=list)
    votes: list = dataclasses.field(default_factory=list)
    autoplaylists: Dict[str, list] = dataclasses.field(default_factory=dict)
    marry: Dict[str, str] = dataclasses.field(default_factory=dict)
    donation: Dict[str, str] = dataclasses.field(default_factory=dict)
    claim: Dict[str, str] = dataclasses.field(default_factory=dict)
    animes: Dict[str, str] = dataclasses.field(default_factory=dict)
    cachedanimes: Dict[str, str] = dataclasses.field(default_factory=dict)
    server_count: Dict[str, int] = dataclasses.field(default_factory=dict)
    source: str = dataclasses.field(default='ytsearch')

class AutoplaylistSettings(Settings):
    songs: list = dataclasses.field(default_factory=list)
    name: str = dataclasses.field(default="")
    created_by: str = dataclasses.field(default="")
    created_by_name: str = dataclasses.field(default="")
    created_date: str = dataclasses.field(default="")
    private: bool = dataclasses.field(default=True)
    shuffle: bool = dataclasses.field(default=True)
    whitelist: list = dataclasses.field(default_factory=list)
    is_personal: bool = dataclasses.field(default=False)
    description: str = dataclasses.field(default="")
    avatar: str = dataclasses.field(default="")
    upvote: list = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class SettingsDB:
    client: Final[motor.motor_asyncio.AsyncIOMotorClient]
    db: Final[motor.motor_asyncio.AsyncIOMotorDatabase]
    guild_settings_collection: Final[motor.motor_asyncio.AsyncIOMotorCollection]
    glob_settings_collection: Final[motor.motor_asyncio.AsyncIOMotorCollection]
    autoplaylist_settings_collection: Final[motor.motor_asyncio.AsyncIOMotorCollection]

    @classmethod
    async def create(cls) -> "SettingsDB":
        client = motor.motor_asyncio.AsyncIOMotorClient(db_host, db_port)
        db = client.Watora
        return cls(client, db, db.settings, db.glob, db.autoplaylists)

    async def get_glob_settings(self) -> GlobSettings:
        document = await self.glob_settings_collection.find_one({"_id": 0})
        if document:
            return dataclasses.replace(GlobSettings(document.get("_id")), **document)
        return GlobSettings(0)

    async def set_glob_settings(self, settings: GlobSettings) -> None:
        await self.glob_settings_collection.replace_one({
