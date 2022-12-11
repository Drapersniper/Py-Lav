from __future__ import annotations

import datetime
import pathlib
import typing
from dataclasses import dataclass

import aiopath  # type: ignore
import ujson
from discord.utils import utcnow

from pylav.extension.bundled_node.utils import get_true_path
from pylav.helpers.singleton import SingletonCachedByKey
from pylav.storage.database.cache.decodators import maybe_cached
from pylav.storage.database.cache.model import CachedModel
from pylav.storage.database.tables.config import LibConfigRow
from pylav.type_hints.dict_typing import JSON_DICT_TYPE, JSON_DICT_WITH_DATE_TYPE


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True, frozen=True)
class Config(CachedModel, metaclass=SingletonCachedByKey):
    bot: int
    id: int = 1

    def get_cache_key(self) -> str:
        return f"{self.bot}:{self.id}"

    @maybe_cached
    async def exists(self) -> bool:
        """Check if the config exists.

        Returns
        -------
        bool
            Whether the config exists.
        """
        return await LibConfigRow.exists().where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))

    @maybe_cached
    async def fetch_config_folder(self) -> str:
        """Fetch the config folder.

        Returns
        -------
        str
            The config folder.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.config_folder)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["config_folder"] if response else LibConfigRow.config_folder.default

    async def update_config_folder(self, config_folder: aiopath.AsyncPath | pathlib.Path | str) -> None:
        """Update the config folder.

        Parameters
        ----------
        config_folder
            The new config folder.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, config_folder)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET config_folder = EXCLUDED.config_folder
            """,
            self.id,
            self.bot,
            str(config_folder),
        )
        await self.update_cache((self.fetch_config_folder, str(config_folder)), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_localtrack_folder(self) -> str:
        """Fetch the localtrack folder.

        Returns
        -------
        str
            The localtrack folder.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.localtrack_folder)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["localtrack_folder"] if response else LibConfigRow.localtrack_folder.default

    async def update_localtrack_folder(self, localtrack_folder: aiopath.AsyncPath | pathlib.Path | str) -> None:
        """Update the localtrack folder.

        Parameters
        ----------
        localtrack_folder
            The new localtrack folder.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, localtrack_folder)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET localtrack_folder = EXCLUDED.localtrack_folder
            """,
            self.id,
            self.bot,
            str(localtrack_folder),
        )
        await self.update_cache((self.fetch_localtrack_folder, str(localtrack_folder)), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_java_path(self) -> str:
        """Fetch the java path.

        Returns
        -------
        str
            The java path.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.java_path)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )

        temp_path = response["java_path"] if response else LibConfigRow.java_path.default
        java_path = get_true_path(temp_path, temp_path)
        return java_path

    async def update_java_path(self, java_path: aiopath.AsyncPath | pathlib.Path | str) -> None:
        """Update the java path.

        Parameters
        ----------
        java_path
            The new java path.
        """
        java_path = get_true_path(java_path, java_path)
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, java_path)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET java_path = EXCLUDED.java_path
            """,
            self.id,
            self.bot,
            str(java_path),
        )
        await self.update_cache((self.fetch_java_path, str(java_path)), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_enable_managed_node(self) -> bool:
        """Fetch the enable_managed_node.

        Returns
        -------
        bool
            The enable_managed_node.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.enable_managed_node)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["enable_managed_node"] if response else LibConfigRow.enable_managed_node.default

    async def update_enable_managed_node(self, enable_managed_node: bool) -> None:
        """Update the enable_managed_node.

        Parameters
        ----------
        enable_managed_node
            The new enable_managed_node.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, enable_managed_node)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET enable_managed_node = EXCLUDED.enable_managed_node
            """,
            self.id,
            self.bot,
            enable_managed_node,
        )
        await self.update_cache((self.fetch_enable_managed_node, enable_managed_node), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_use_bundled_pylav_external(self) -> bool:
        """Fetch the use_bundled_pylav_external.

        Returns
        -------
        bool
            The use_bundled_pylav_external.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.use_bundled_pylav_external)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["use_bundled_pylav_external"] if response else LibConfigRow.use_bundled_pylav_external.default

    async def update_use_bundled_pylav_external(self, use_bundled_pylav_external: bool) -> None:
        """Update the use_bundled_pylav_external.

        Parameters
        ----------
        use_bundled_pylav_external
            The new use_bundled_pylav_external.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, use_bundled_pylav_external)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET use_bundled_pylav_external = EXCLUDED.use_bundled_pylav_external
            """,
            self.id,
            self.bot,
            use_bundled_pylav_external,
        )
        await self.update_cache(
            (self.fetch_use_bundled_pylav_external, use_bundled_pylav_external), (self.exists, True)
        )
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_use_bundled_lava_link_external(self) -> bool:
        """Fetch the use_bundled_lava_link_external.

        Returns
        -------
        bool
            The use_bundled_lava_link_external.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.use_bundled_lava_link_external)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return (
            response["use_bundled_lava_link_external"]
            if response
            else LibConfigRow.use_bundled_lava_link_external.default
        )

    async def update_use_bundled_lava_link_external(self, use_bundled_lava_link_external: bool) -> None:
        """Update the use_bundled_lava_link_external.

        Parameters
        ----------
        use_bundled_lava_link_external
            The new use_bundled_lava_link_external.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, use_bundled_lava_link_external)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET use_bundled_lava_link_external = EXCLUDED.use_bundled_lava_link_external
            """,
            self.id,
            self.bot,
            use_bundled_lava_link_external,
        )
        await self.update_cache(
            (self.fetch_use_bundled_lava_link_external, use_bundled_lava_link_external), (self.exists, True)
        )
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_download_id(self) -> int:
        """Fetch the download_id.

        Returns
        -------
        str
            The download_id.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.download_id)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["download_id"] if response else LibConfigRow.download_id.default

    async def update_download_id(self, download_id: int) -> None:
        """Update the download_id.

        Parameters
        ----------
        download_id
            The new download_id.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, download_id)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET download_id = EXCLUDED.download_id
            """,
            self.id,
            self.bot,
            download_id,
        )
        await self.update_cache((self.fetch_download_id, download_id), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_extras(self) -> JSON_DICT_TYPE:
        """Fetch the extras.

        Returns
        -------
        dict
            The extras.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.extras)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["extras"] if response else ujson.loads(LibConfigRow.extras.default)

    async def update_extras(self, extras: JSON_DICT_TYPE) -> None:
        """Update the extras.

        Parameters
        ----------
        extras
            The new extras.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, extras)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET extras = EXCLUDED.extras
            """,
            self.id,
            self.bot,
            ujson.dumps(extras),
        )
        await self.update_cache((self.fetch_extras, extras), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_next_execution_update_bundled_playlists(self) -> datetime.datetime:
        """Fetch the next_execution_update_bundled_playlists.

        Returns
        -------
        datetime.datetime
            The next_execution_update_bundled_playlists.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.next_execution_update_bundled_playlists)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["next_execution_update_bundled_playlists"] if response else utcnow()

    async def update_next_execution_update_bundled_playlists(self, next_execution: datetime.datetime) -> None:
        """Update the next_execution_update_bundled_playlists.

        Parameters
        ----------
        next_execution
            The new next_execution_update_bundled_playlists.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, next_execution_update_bundled_playlists)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET next_execution_update_bundled_playlists = EXCLUDED.next_execution_update_bundled_playlists
            """,
            self.id,
            self.bot,
            next_execution,
        )
        await self.update_cache(
            (self.fetch_next_execution_update_bundled_playlists, next_execution), (self.exists, True)
        )
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_next_execution_update_bundled_external_playlists(self) -> datetime.datetime:
        """Fetch the next_execution_update_bundled_external_playlists.

        Returns
        -------
        datetime.datetime
            The next_execution_update_bundled_external_playlists.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.next_execution_update_bundled_external_playlists)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["next_execution_update_bundled_external_playlists"] if response else utcnow()

    async def update_next_execution_update_bundled_external_playlists(self, next_execution: datetime.datetime) -> None:
        """Update the next_execution_update_bundled_external_playlists.

        Parameters
        ----------
        next_execution
            The new next_execution.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252

        # noinspection PyPep8
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, next_execution_update_bundled_external_playlists)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE
            SET next_execution_update_bundled_external_playlists = EXCLUDED.next_execution_update_bundled_external_playlists
            """,  # noqa
            self.id,
            self.bot,
            next_execution,
        )
        await self.update_cache(
            (self.fetch_next_execution_update_bundled_external_playlists, next_execution), (self.exists, True)
        )
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_next_execution_update_external_playlists(self) -> datetime.datetime:
        """Fetch the next_execution_update_external_playlists.

        Returns
        -------
        datetime.datetime
            The next_execution_update_external_playlists.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.next_execution_update_external_playlists)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["next_execution_update_external_playlists"] if response else utcnow()

    async def update_next_execution_update_external_playlists(self, next_execution: datetime.datetime) -> None:
        """Update the next_execution_update_external_playlists.

        Parameters
        ----------
        next_execution
            The new next_execution.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, next_execution_update_external_playlists)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET next_execution_update_external_playlists = EXCLUDED.next_execution_update_external_playlists
            """,
            self.id,
            self.bot,
            next_execution,
        )
        await self.update_cache(
            (self.fetch_next_execution_update_external_playlists, next_execution), (self.exists, True)
        )
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_update_bot_activity(self) -> bool:
        """Fetch the update_bot_activity.

        Returns
        -------
        bool
            The update_bot_activity.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.update_bot_activity)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["update_bot_activity"] if response else LibConfigRow.update_bot_activity.default

    async def update_update_bot_activity(self, update_bot_activity: bool) -> None:
        """Update the update_bot_activity.

        Parameters
        ----------
        update_bot_activity
            The new update_bot_activity.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, update_bot_activity)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET update_bot_activity = EXCLUDED.update_bot_activity
            """,
            self.id,
            self.bot,
            update_bot_activity,
        )
        await self.update_cache((self.fetch_update_bot_activity, update_bot_activity), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    @maybe_cached
    async def fetch_auto_update_managed_nodes(self) -> bool:
        """Fetch the auto_update_managed_nodes.

        Returns
        -------
        bool
            The auto_update_managed_nodes.
        """
        response = (
            await LibConfigRow.select(LibConfigRow.auto_update_managed_nodes)
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True)
        )
        return response["auto_update_managed_nodes"] if response else LibConfigRow.auto_update_managed_nodes.default

    async def update_auto_update_managed_nodes(self, auto_update_managed_nodes: bool) -> None:
        """Update the auto_update_managed_nodes.

        Parameters
        ----------
        auto_update_managed_nodes
            The new auto_update_managed_nodes.
        """
        # TODO: When piccolo add support to on conflict clauses using RAW here is more efficient
        #  Tracking issue: https://github.com/piccolo-orm/piccolo/issues/252
        await LibConfigRow.raw(
            """
            INSERT INTO lib_config (id, bot, auto_update_managed_nodes)
            VALUES ({}, {}, {})
            ON CONFLICT (id, bot)
            DO UPDATE SET auto_update_managed_nodes = EXCLUDED.auto_update_managed_nodes
            """,
            self.id,
            self.bot,
            auto_update_managed_nodes,
        )
        await self.update_cache((self.fetch_auto_update_managed_nodes, auto_update_managed_nodes), (self.exists, True))
        await self.invalidate_cache(self.fetch_all)

    async def delete(self) -> None:
        """Delete the config from the database"""
        await LibConfigRow.delete().where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
        await self.invalidate_cache()

    @maybe_cached
    async def fetch_all(self) -> JSON_DICT_WITH_DATE_TYPE:
        """Update all attributed for the config from the database.

        Returns
        -------
        Config
            The updated config.
        """
        data = typing.cast(
            JSON_DICT_TYPE,
            await LibConfigRow.select()
            .where((LibConfigRow.id == self.id) & (LibConfigRow.bot == self.bot))
            .first()
            .output(load_json=True, nested=True),
        )
        if data:
            data["java_path"] = get_true_path(data["java_path"], data["java_path"])
            return data

        return {
            "id": self.id,
            "bot": self.bot,
            "config_folder": LibConfigRow.config_folder.default,
            "java_path": get_true_path(LibConfigRow.java_path.default),
            "enable_managed_node": LibConfigRow.enable_managed_node.default,
            "auto_update_managed_nodes": LibConfigRow.auto_update_managed_nodes.default,
            "localtrack_folder": LibConfigRow.localtrack_folder.default,
            "download_id": LibConfigRow.download_id.default,
            "update_bot_activity": LibConfigRow.update_bot_activity.default,
            "use_bundled_pylav_external": LibConfigRow.use_bundled_pylav_external.default,
            "use_bundled_lava_link_external": LibConfigRow.use_bundled_lava_link_external.default,
            "extras": ujson.loads(LibConfigRow.extras.default),
            "next_execution_update_bundled_playlists": LibConfigRow.next_execution_update_bundled_playlists.default,
            "next_execution_update_bundled_external_playlists": LibConfigRow.next_execution_update_bundled_external_playlists.default,  # noqa
            "next_execution_update_external_playlists": LibConfigRow.next_execution_update_external_playlists.default,
        }
