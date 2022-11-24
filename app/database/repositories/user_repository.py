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

from typing import Optional
from neo4j import Record, AsyncResult

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.user import User


class UserRepository(BaseRepository):

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = f"""
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE id(user) = {user_id}
            RETURN user, phone
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        if not record:
            return None

        user = User(
            id=user_id,
            phone=record["phone"]["number"],
            username=record["user"]["username"],
            is_blocked=record["user"]["is_blocked"],
        )

        return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = f"""
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE user.username = "{username}"
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        if not record:
            return None

        user = User(
            id=record["user_id"],
            phone=record["phone"]["number"],
            username=username,
            is_blocked=record["user"]["is_blocked"],
        )

        return user

    async def is_exists(self, username: str) -> bool:
        user: User | None = await self.get_user_by_username(username)
        if user:
            return True

        return False
