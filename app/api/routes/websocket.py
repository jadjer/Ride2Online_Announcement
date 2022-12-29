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

from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_filter import get_events_filter
from app.api.dependencies.get_from_path import get_event_id_from_path
from app.api.dependencies.manager import get_connection_manager
from app.database.repositories.event_repository import EventRepository
from app.manager.connection_manager import ConnectionManager
from app.models.domain.user import User
from app.models.schemas.event import EventsFilter, EventResponse, EventsResponse, EventCreate, EventUpdate
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings

router = APIRouter()


@router.websocket("")
async def websocket_events(
        websocket: WebSocket,
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
        manager: ConnectionManager = Depends(get_connection_manager)
) -> None:
    logger.info(f"New user connection {user.id}")

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{user.id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{user.id} left the chat")
