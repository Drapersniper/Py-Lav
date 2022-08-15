[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Drapersniper/Py-Lav/master.svg)](https://results.pre-commit.ci/latest/github/Drapersniper/Py-Lav/master)
[![GitHub license](https://img.shields.io/github/license/Drapersniper/Py-Lav.svg)](https://github.com/Drapersniper/Py-Lav/blob/master/LICENSE)
[![Support Server](https://img.shields.io/discord/970987707834720266)](https://discord.com/invite/Sjh2TSCYQB)
[![PyPi](https://img.shields.io/pypi/v/Py-Lav?style=plastic)](https://pypi.org/project/Py-Lav/)

# Documentation
### Installation
 - [Click Here](./SETUP.md)
---------------------------
### Requirements
- PostgresSQL 14 server
  - MacOS: [PostgresSQL](https://www.postgresql.org/download/macosx/)
  - Windows: [PostgresSQL](https://www.postgresql.org/download/windows/)
  - Linux: [PostgresSQL](https://www.postgresql.org/download/linux/)
- Python 3.10+ (On initial release - during pre-alpha phase 3.9+)
- [Discord.py](https://github.com/Rapptz/discord.py) 2.0.0+ bot

### Environment Variables
Note - All environment variables except `PYLAV__LOGGER_PREFIX` can be configured from the `pylav.yaml` file which should reside in the home directory of the user running the bot.
An example of the file can be found at [pylav.example.yaml](./pylav.example.yaml), if you don't create the file yourself pylav will do so on the first run, and once the file exists it will be preferred over the Environment Variable set.
#### Required
- Env Vars to connect the lib to the PostgresSQL server
  All Envvars default to AsyncPG [defaults](https://magicstack.github.io/asyncpg/current/api/index.html#connection)
  - PYLAV__POSTGRES_PORT
  - PYLAV__POSTGRES_PASSWORD
  - PYLAV__POSTGRES_USER
  - PYLAV__POSTGRES_DB
  - PYLAV__POSTGRES_HOST
#### Optional
- Env Vars to connect the lib cache to Redis, note if these are missing the library will default to PostgresSQL, therefore they are not necessary.
    - This will be used by the aiohttp cached client session for storing cached responses for 1 day, this reduces stress on some of the requests the lib makes such as to RadioBrowser.
      - PYLAV__REDIS_FULL_ADDRESS_RESPONSE_CACHE
        - e.g. redis://[[username]:[password]]@localhost:6379/0
        - e.g. unix://[[username]:[password]]@/path/to/socket.sock?db=0
- Misc
  - PYLAV__LOGGER_PREFIX - Sets the logger prefix, defaults to None, or "red." if [redbot](https://github.com/Cog-Creators/Red-DiscordBot) is installed.
  - PYLAV__JAVA_EXECUTABLE - Sets the Java executable to be used by PyLav for the managed Lavalink node
  - PYLAV__USE_BUNDLED_EXTERNAL_NODES - Set this to 1 to enable the bundled external nodes or 0 to disabled it
- Unmanaged External Node - If both PYLAV__EXTERNAL_UNMANAGED_HOST and PYLAV__EXTERNAL_UNMANAGED_PASSWORD are set then the managed node is not started up
  - PYLAV__EXTERNAL_UNMANAGED_HOST - No Default - Required (Should not contain the protocol i.e "http" or "https", this is determined by PYLAV__EXTERNAL_UNMANAGED_SSL)
  - PYLAV__EXTERNAL_UNMANAGED_PASSWORD - No Default - Required
  - PYLAV__EXTERNAL_UNMANAGED_PORT - Defaults to 80
  - PYLAV__EXTERNAL_UNMANAGED_SSL - Defaults to 0 (i.e False) - Possible values are 0 - 1
---------------------------
## Supported sources
### [Built-in](https://github.com/freyacodes/Lavalink):
  - youtube
  - soundcloud
  - twitch
  - bandcamp
  - vimeo
  - http
  - local
### With [Topis-Source-Managers-Plugin](https://github.com/Topis-Lavalink-Plugins/Topis-Source-Managers-Plugin):
  - spotify
  - applemusic
### With [DuncteBot-plugin](https://github.com/DuncteBot/skybot-lavalink-plugin):
  - getyarn
  - clypit
  - tts
  - pornhub
  - reddit
  - ocremix
  - tiktok
  - mixcloud
### With [Google Cloud TTS](https://github.com/DuncteBot/tts-plugin):
  - gcloud-tts
### With [Sponsorblock-Plugin](https://github.com/Topis-Lavalink-Plugins/Sponsorblock-Plugin):
  - sponsorblock

## Supported Lavalink features
  - Supports all features of [Lavalink](https://github.com/freyacodes/Lavalink)
    - Filters
    - IP Rotation
    - Plug-ins

Features
---------------------------
- Multiple node support
  - Node region assignment based on IP
- Track cache for the last 30 days to reduce the number of duplicated queries
- Managed local node with auto-restart and auto update
- Many helper methods and functions
- Support for multiple cogs to access the library at once
- Playlists and EQ saved at a library level to be shared with cogs
- Player state persistence
    - Upon library state being shutdown all player states are saved and restored on library startup
- History of played tracks available for players
- RadioBrowser.org API to retrieve radio stations available for players
- M3U, PLS and PYLAV text file parser to convert contents into a playlist (p.s. Lavalink must support the format/coded of files still)


Credits
---------------------------
- [Devoxin- Lavalink.py](https://github.com/Devoxin/Lavalink.py) for ideas for implementation.
- [globocom/m3u8](https://github.com/globocom/m3u8) for the M3U8 parser which I made asynchronous found in [m3u8_parser](./pylav/m3u8_parser).
- [andreztz/pyradios](https://github.com/andreztz/pyradios) for the radio parser which I made asynchronous found in [radio](./pylav/radio).
