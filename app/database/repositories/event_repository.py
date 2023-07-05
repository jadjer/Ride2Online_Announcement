#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
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

    async def create_event_by_user_id(
            self,
            user_id: int,
            *,
            title: str,
            subtitle: str = "",
            text: str,
            picture: HttpUrl,
            location: Location,
            start_at: datetime,
            **kwargs
    ) -> Event | None:
        query = """
            MATCH (user:User)
            WHERE id(user) = $user_id
            CREATE (event:Event)-[:Author]->(user)
            CREATE (event)-[:LocatedAt]->(location:Location)
            SET event.title = $title
            SET event.subtitle = $subtitle
            SET event.text = $text
            SET event.picture = $picture
            SET event.start_at = $start_at
            SET event.created_at = $created_at
            SET event.updated_at = $updated_at
            SET location.name = $location.name
            SET location.description = $location.description
            SET location.address = $location.address
            SET location.latitude = $location.latitude
            SET location.longitude = $location.longitude
            RETURN id(event) AS event_id, event, location
        """

        event = Event(title=title, subtitle=subtitle, text=text, picture=picture, location=location, start_at=start_at)
        event.created_at = datetime.now().timestamp()
        event.updated_at = datetime.now().timestamp()

        result: AsyncResult = await self.session.run(query, user_id=user_id, **event.dict())

        try:
            record: Record | None = await result.single()
        except ConstraintError as exception:
            logger.warning(exception)
            return None

        return self.get_event_from_record(record)

    async def get_events(self, limit: int, offset: int) -> List[Event]:
        query = """
            MATCH (event:Event)-[:LocatedAt]->(location:Location)
            RETURN id(event) AS event_id, event, location
            LIMIT $limit
        """

        result: AsyncResult = await self.session.run(query, limit=limit)

        events: List[Event] = []

        async for record in result:
            event = self.get_event_from_record(record)
            events.append(event)

        return events

    async def get_event_by_id(self, event_id: int) -> Event | None:
        query = """
            MATCH (event:Event)-[:LocatedAt]->(location:Location)
            WHERE id(event) = $event_id
            RETURN id(event) AS event_id, event, location
        """

        result: AsyncResult = await self.session.run(query, event_id=event_id)
        record: Record | None = await result.single()

        return self.get_event_from_record(record)

    async def get_event_by_title(self, title: str) -> Event | None:
        query = """
            MATCH (event:Event {title: $title})-[:LocatedAt]->(location:Location)
            RETURN id(event) AS event_id, event, location
        """

        result: AsyncResult = await self.session.run(query, title=title)
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
            picture: str | None = None,
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

        query = """
            MATCH (location:Location)<-[:LocatedAt]-(event:Event)-[:Author]->(user:User)
            WHERE id(event) = $event_id AND id(user) = $user_id
            SET event.title = $title
            SET event.subtitle = $subtitle
            SET event.text = $text
            SET event.picture = $picture
            SET event.start_at = $start_at
            SET event.created_at = $created_at
            SET event.updated_at = $updated_at
            SET location.name = $location.name
            SET location.description = $location.description
            SET location.address = $location.address
            SET location.latitude = $location.latitude
            SET location.longitude = $location.longitude
            RETURN id(event) AS event_id, event, location
        """
        await self.session.run(query, user_id=user_id, event_id=event_id, **event.dict())

        return await self.get_event_by_id(event_id)

    async def delete_event_by_id(self, user_id: int, event_id: int) -> None:
        query = """
            MATCH (event:Event)-[:Author]->(user:User)
            WHERE id(event) = $event_id AND id(user) = $user_id
            DETACH DELETE event
        """
        await self.session.run(query, user_id=user_id, event_id=event_id)

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
            start_at=datetime.fromisoformat(record["event"]["start_at"]),
            created_at=datetime.fromtimestamp(record["event"]["created_at"]),
            updated_at=datetime.fromtimestamp(record["event"]["updated_at"]),
        )

        return event
