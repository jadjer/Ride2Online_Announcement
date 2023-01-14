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

from datetime import datetime
from loguru import logger
from typing import List

from neo4j import AsyncResult, Record
from neo4j.exceptions import ConstraintError
from pydantic import HttpUrl

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.event import Event
from app.models.domain.location import Location


class EventRepository(BaseRepository):

    async def create_event_by_user_id(self, user_id: int, *,
                                      title: str,
                                      subtitle: str = "",
                                      text: str = "",
                                      picture: HttpUrl,
                                      location: Location,
                                      start_at: datetime,
                                      **kwargs) -> Event | None:
        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            CREATE (event:Event)-[:Author]->(user)
            CREATE (event)-[:LocatedAt]->(location:Location)
            SET event.title = "{title}"
            SET event.subtitle = "{subtitle}"
            SET event.text = "{text}"
            SET event.picture = "{picture}"
            SET event.start_at = "{start_at}"
            SET event.created_at = "{datetime.now()}"
            SET event.updated_at = "{datetime.now()}"
            SET location.name = "{location.name}"
            SET location.description = "{location.description}"
            SET location.address = "{location.address}"
            SET location.latitude = "{location.latitude}"
            SET location.longitude = "{location.longitude}"
            RETURN id(event) AS event_id, event, location
        """

        result: AsyncResult = await self.session.run(query)

        try:
            record: Record | None = await result.single()
        except ConstraintError as exception:
            logger.warning(exception)
            return None

        return self.get_event_from_record(record)

    async def get_events(self, limit: int, offset: int) -> List[Event]:
        query = f"""
            MATCH (event:Event)-[:LocatedAt]->(location:Location)
            RETURN id(event) AS event_id, event, location
            LIMIT {limit}
        """

        result: AsyncResult = await self.session.run(query)

        events: List[Event] = []

        async for record in result:
            event = self.get_event_from_record(record)
            events.append(event)

        return events

    async def get_event_by_id(self, event_id: int) -> Event | None:
        query = f"""
            MATCH (event:Event)-[:LocatedAt]->(location:Location)
            WHERE id(event) = {event_id}
            RETURN id(event) AS event_id, event, location
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        return self.get_event_from_record(record)

    async def get_event_by_title(self, title: str) -> Event | None:
        query = f"""
            MATCH (event:Event)-[:LocatedAt]->(location:Location)
            WHERE event.title = "{title}"
            RETURN id(event) AS event_id, event, location
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        return self.get_event_from_record(record)

    async def update_event_by_id(
            self,
            user_id: int,
            event_id: int,
            *,
            title: str | None = None,
            subtitle: str | None = None,
            text: str | None = None,
            picture: HttpUrl | None = None,
            location: Location | None = None,
            start_at: datetime | None = None,
            **kwargs
    ) -> Event | None:
        event = await self.get_event_by_id(event_id)
        if not event:
            return event

        event.title = title or event.title
        event.subtitle = subtitle or event.subtitle
        event.text = text or event.text
        event.picture = picture or event.picture
        event.location = location or event.location
        event.start_at = start_at or event.start_at
        event.created_at = event.created_at
        event.updated_at = datetime.now()

        query = f"""
            MATCH (location:Location)<-[:LocatedAt]-(event:Event)-[:Author]->(user:User)
            WHERE id(event) = {event_id} AND id(user) = {user_id}
            SET event.title = "{event.title}"
            SET event.subtitle = "{event.subtitle}"
            SET event.text = "{event.text}"
            SET event.picture = "{event.picture}"
            SET event.start_at = "{event.start_at}"
            SET event.created_at = "{event.created_at}"
            SET event.updated_at = "{event.updated_at}"
            SET location.name = "{event.location.name}"
            SET location.description = "{event.location.description}"
            SET location.address = "{event.location.address}"
            SET location.latitude = "{event.location.latitude}"
            SET location.longitude = "{event.location.longitude}"
            RETURN id(event) AS event_id, event, location
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

    @staticmethod
    def get_event_from_record(record: Record) -> Event | None:
        if not record:
            return None

        location = Location(
            name=record["location"]["name"],
            description=record["location"]["description"],
            address=record["location"]["address"],
            latitude=record["location"]["latitude"],
            longitude=record["location"]["longitude"],
        )

        event = Event(
            id=record["event_id"],
            title=record["event"]["title"],
            subtitle=record["event"]["subtitle"],
            text=record["event"]["text"],
            picture=record["event"]["picture"],
            location=location,
            start_at=record["event"]["start_at"],
            created_at=record["event"]["created_at"],
            updated_at=record["event"]["updated_at"]
        )

        return event
