#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from loguru import logger
from typing import List

from neo4j import AsyncResult, Record
from neo4j.exceptions import ConstraintError

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.event import Event


class EventRepository(BaseRepository):

    async def create_event_by_user_id(self, user_id: int, *, title: str, **kwargs) -> Event | None:
        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            CREATE (event:Event)-[:Author]->(user)
            SET event.title = "{title}"
            RETURN id(event) AS event_id, event
        """

        result: AsyncResult = await self.session.run(query)

        try:
            record: Record | None = await result.single()
        except ConstraintError as exception:
            logger.warning(exception)
            return None

        if not record:
            logger.warning("Query result is empty")
            return None

        event = Event(
            id=record["event_id"],
            title=record["event"]["title"]
        )

        return event

    async def get_events(self, limit: int, offset: int) -> List[Event]:
        query = f"""
            MATCH (event:Event)
            RETURN id(event) AS event_id, event
            LIMIT {limit}
        """

        result: AsyncResult = await self.session.run(query)

        events: List[Event] = []

        async for record in result:
            event = Event(
                id=record["event_id"],
                title=record["event"]["title"],
            )
            events.append(event)

        return events

    async def get_event_by_id(self, event_id: int) -> Event | None:
        query = f"""
            MATCH (event:Event)
            WHERE id(event) = {event_id}
            RETURN event
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        if not record:
            return None

        event = Event(
            id=event_id,
            title=record["event"]["title"]
        )

        return event

    async def get_event_by_title(self, title: str) -> Event | None:
        query = f"""
            MATCH (event:Event)
            WHERE event.title = "{title}"
            RETURN id(event) AS event_id, event
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        if not record:
            return None

        event = Event(
            id=record["event_id"],
            title=record["event"]["title"]
        )

        return event

    async def update_event_by_id(
            self,
            user_id: int,
            event_id: int,
            *,
            title: str | None = None,
            **kwargs
    ) -> Event | None:
        event = await self.get_event_by_id(event_id)
        if not event:
            return event

        event.title = title or event.title

        query = f"""
            MATCH (event:Event)-[:Author]->(user:User)
            WHERE id(event) = {event_id} AND id(user) = {user_id}
            SET event.title = "{event.title}"
        """
        await self.session.run(query)

        return await self.get_event_by_id(event_id)

    async def delete_event_by_id(self, user_id: int, event_id: int) -> None:
        query = f"""
            MATCH (event:Event)-[:Author]->(user:User)
            WHERE id(event) = {event_id} AND id(user) = {user_id}
            DETACH DELETE event
        """
        await self.session.run(query)
