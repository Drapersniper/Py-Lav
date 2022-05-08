from __future__ import annotations

import asyncio
import operator
from typing import TYPE_CHECKING

import aiohttp
import ujson

from pylav._logging import getLogger
from pylav.constants import DEFAULT_REGIONS
from pylav.events import NodeConnectedEvent, NodeDisconnectedEvent
from pylav.node import Node
from pylav.player import Player

if TYPE_CHECKING:
    from pylav.client import Client

LOGGER = getLogger("red.PyLink.NodeManager")


class NodeManager:
    def __init__(self, client: Client):
        self._client = client
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), json_serialize=ujson.dumps)
        self._player_queue = []

        self._nodes = []
        self._adding_nodes = asyncio.Event()

    def __iter__(self):
        yield from self._nodes

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    @property
    def client(self) -> Client:
        """Returns the client."""
        return self._client

    @property
    def nodes(self) -> list[Node]:
        """Returns a list of all nodes."""
        return self._nodes

    @property
    def available_nodes(self) -> list[Node]:
        """Returns a list of available nodes."""
        return list(filter(operator.attrgetter("available"), self.nodes))

    @property
    def managed_nodes(self) -> list[Node]:
        """Returns a list of nodes that are managed by the client."""
        return list(filter(operator.attrgetter("managed"), self.nodes))

    @property
    def search_only_nodes(self) -> list[Node]:
        """Returns a list of nodes that are search only."""
        return list(filter(operator.attrgetter("available", "search_only"), self.nodes))

    @property
    def player_queue(self) -> list[Player]:
        """Returns a list of players that are queued to be played."""
        return self._player_queue

    @player_queue.setter
    def player_queue(self, players: list[Player]) -> None:
        """Sets the player queue."""
        self._player_queue = players

    @player_queue.deleter
    def player_queue(self):
        """Clears the player queue."""
        self._player_queue.clear()

    async def add_node(
        self,
        *,
        host: str,
        port: int,
        password: str,
        unique_identifier: int,
        name: str,
        resume_key: str = None,
        resume_timeout: int = 60,
        reconnect_attempts: int = -1,
        ssl: bool = False,
        search_only: bool = False,
        skip_db: bool = False,
        disabled_sources: list[str] = None,
        managed: bool = False,
        yaml: dict | None = None,
        extras: dict = None,
    ) -> Node:
        """
        Adds a node to PyLink's node manager.
        Parameters
        ----------
        host: :class:`str`
            The address of the Lavalink node.
        port: :class:`int`
            The port to use for websocket and REST connections.
        password: :class:`str`
            The password used for authentication.
        resume_key: Optional[:class:`str`]
            A resume key used for resuming a session upon re-establishing a WebSocket connection to Lavalink.
            Defaults to `None`.
        resume_timeout: Optional[:class:`int`]
            How long the node should wait for a connection while disconnected before clearing all players.
            Defaults to `60`.
        name: :class:`str`
            An identifier for the node that will show in logs. Defaults to `None`.
        reconnect_attempts: Optional[:class:`int`]
            The amount of times connection with the node will be reattempted before giving up.
            Set to `-1` for infinite. Defaults to `3`.
        ssl: Optional[:class:`bool`]
            Whether to use a ssl connection. Defaults to `False`.
        search_only: :class:`bool`
            Whether the node is search only. Defaults to `False`.
        unique_identifier: Optional[:class:`str`]
            A unique identifier for the node. Defaults to `None`.
        skip_db: Optional[:class:`bool`]
            Whether to skip the database creation op. Defaults to `False`.
        disabled_sources: Optional[:class:`list`[:class:`str`]]
            A list of sources to disable. Defaults to `None`.
        managed: Optional[:class:`bool`]
            Whether the node is managed by the client. Defaults to `False`.
        yaml: Optional[:class:`dict`]
            A dictionary of node settings. Defaults to `None`.
        extras: Optional[:class:`dict`]
            A dictionary of extra settings. Defaults to `{}`.
        """
        node = Node(
            manager=self,
            host=host,
            port=port,
            password=password,
            resume_key=resume_key,
            resume_timeout=resume_timeout,
            name=name,
            reconnect_attempts=reconnect_attempts,
            ssl=ssl,
            search_only=search_only,
            unique_identifier=unique_identifier,
            disabled_sources=disabled_sources,
            managed=managed,
            extras=extras or {},
        )
        self._nodes.append(node)

        LOGGER.info("[NODE-%s] Successfully added to Node Manager", node.name)
        LOGGER.verbose("[NODE-%s] Successfully added to Node Manager -- %r", node.name, node)
        node._config = (
            await self.client.node_db_manager.get_node_config(unique_identifier)
            if skip_db
            else await self.client.node_db_manager.add_node(
                host=host,
                port=port,
                password=password,
                resume_key=resume_key,
                resume_timeout=resume_timeout,
                name=name,
                reconnect_attempts=reconnect_attempts,
                ssl=ssl,
                search_only=search_only,
                unique_identifier=unique_identifier,
                disabled_sources=disabled_sources,
                managed=managed,
                yaml=yaml,
                extras=extras or {},
            )
        )

        return node

    async def remove_node(self, node: Node) -> None:
        """
        Removes a node.
        Parameters
        ----------
        node: :class:`Node`
            The node to remove from the list.
        """
        await node.close()
        self.nodes.remove(node)
        LOGGER.info("[NODE-%s] Successfully removed Node", node.name)
        LOGGER.verbose("[NODE-%s] Successfully removed Node -- %r", node.name, node)
        if node.identifier and not node.managed:
            await self.client.node_db_manager.delete(node.identifier)
            LOGGER.debug("[NODE-%s] Successfully deleted Node from database", node.name)

    def get_region(self, endpoint: str | None) -> str | None:
        """
        Returns a region from a Discord voice server address.
        Parameters
        ----------
        endpoint: :class:`str`
            The address of the Discord voice server.
        Returns
        -------
        Optional[:class:`str`]
        """
        if not endpoint:
            return None

        endpoint = endpoint.replace("vip-", "")

        for key in DEFAULT_REGIONS:
            nodes = [n for n in self.available_nodes if n.region == key]

            if not nodes:
                continue

            if endpoint.startswith(key):
                return key
        return None

    def find_best_node(
        self,
        region: str = None,
        not_region: str = None,
        feature: str = None,
        already_attempted_regions: set[str] = None,
    ) -> Node | None:
        """
        Finds the best (least used) node in the given region, if applicable.
        Parameters
        ----------
        region: Optional[:class:`str`]
            The region to find a node in. Defaults to `None`.
        not_region: Optional[:class:`str`]
            The region to exclude from the search. Defaults to `None`.
        feature: Optional[:class:`str`]
            The feature to check for. Defaults to `None`.

            Supported capabilities:
                Built-in:
                    youtube
                    soundcloud
                    twitch
                    bandcamp
                    vimeo
                    http
                    local
                With Topis-Source-Managers-Plugin:
                    spotify
                    applemusic
                With DuncteBot-plugin:
                    getyarn
                    clypit
                    tts
                    pornhub
                    reddit
                    ocremix
                    tiktok
                    mixcloud
                With Google Cloud TTS:
                    gcloud-tts
                With sponsorblock:
                    sponsorblock
        already_attempted_regions: Optional[:class:`set`]
            A set of regions that have already been attempted. Defaults to `None`.
        Returns
        -------
        Optional[:class:`Node`]
        """
        already_attempted_regions = already_attempted_regions or set()
        if feature:
            nodes = [n for n in self.available_nodes if n.has_capability(feature)]
        else:
            nodes = self.available_nodes

        if region and not_region:
            nodes = [
                n
                for n in nodes
                if n.region == region and n.region != not_region and n.region not in already_attempted_regions
            ]
        elif region:
            nodes = [n for n in nodes if n.region == region and n.region not in already_attempted_regions]
        else:
            nodes = [n for n in nodes if n.region != not_region and n.region not in already_attempted_regions]

        if not nodes:
            if feature:
                nodes = [
                    n
                    for n in self.available_nodes
                    if n.has_capability(feature) and n.region not in already_attempted_regions
                ]
            else:
                nodes = self.available_nodes
        if not nodes:
            return None
        return min(nodes, key=operator.attrgetter("penalty"))

    def get_node_by_id(self, unique_identifier: int) -> Node | None:
        """
        Returns a node by its unique identifier.
        Parameters
        ----------
        unique_identifier: :class:`int`
            The unique identifier of the node.
        Returns
        -------
        Optional[:class:`Node`]
        """
        return next((n for n in self.nodes if n.identifier == unique_identifier), None)

    async def node_connect(self, node: Node) -> None:
        """
        Called when a node is connected from Lavalink.
        Parameters
        ----------
        node: :class:`Node`
            The node that has just connected.
        """
        LOGGER.info("[NODE-%s] Successfully established connection", node.name)

        for player in self.player_queue:
            await player.change_node(node)
            LOGGER.debug("[NODE-%s] Successfully moved %s", node.name, player.guild_id)

        if self.client._connect_back:
            for player in node._original_players:
                await player.change_node(node)
                player._original_node = None

        del self.player_queue
        self.client.dispatch_event(NodeConnectedEvent(node))

    async def node_disconnect(self, node: Node, code: int, reason: str) -> None:
        """
        Called when a node is disconnected from Lavalink.
        Parameters
        ----------
        node: :class:`Node`
            The node that has just connected.
        code: :class:`int`
            The code for why the node was disconnected.
        reason: :class:`str`
            The reason why the node was disconnected.
        """
        if self.client.is_shutting_down:
            return
        LOGGER.warning("[NODE-%s] Disconnected with code %s and reason %s", node.name, code, reason)
        LOGGER.verbose(
            "[NODE-%s] Disconnected with code %s and reason %s -- %r",
            node.name,
            code,
            reason,
            node,
        )
        self.client.dispatch_event(NodeDisconnectedEvent(node, code, reason))
        best_node = self.find_best_node(region=node.region)

        if not best_node:
            self.player_queue.extend(node.players)
            LOGGER.error("Unable to move players, no available nodes! Waiting for a node to become available.")
            return

        for player in node.players:
            await player.change_node(best_node)

            if self.client._connect_back:
                player._original_node = node

    async def close(self) -> None:
        await self.session.close()
        for node in self.nodes:
            await node.close()

    async def connect_to_all_nodes(self) -> None:
        nodes_list = []
        for node in await self.client.node_db_manager.get_all_unamanaged_nodes():
            try:
                connection_arguments = node.get_connection_args()
                nodes_list.append(await self.add_node(**connection_arguments, skip_db=True))
            except (ValueError, KeyError) as exc:
                LOGGER.warning(
                    "[NODE-%s] Invalid node, skipping ... id: %s - Original error: %s", node.name, node.id, exc
                )
                continue
        tasks = [asyncio.create_task(n.wait_until_ready()) for n in nodes_list]
        if self.client.enable_managed_node:
            tasks.append(asyncio.create_task(self.client._local_node_manager.wait_until_connected()))
        if not tasks:
            LOGGER.warning("No nodes found, please add some nodes.")
            return
        done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        for task in pending:
            task.cancel()
        for result in done:
            result.result()
        if not self._adding_nodes.is_set():
            self._adding_nodes.set()

    async def wait_until_ready(self, timeout: float | None = None):
        await asyncio.wait_for(self._adding_nodes.wait(), timeout=timeout)
