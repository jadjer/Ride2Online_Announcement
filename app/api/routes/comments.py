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

from fastapi import APIRouter, Depends, status, HTTPException

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_filter import get_events_filter
from app.api.dependencies.get_from_path import get_event_id_from_path
from app.database.repositories.event_repository import EventRepository
from app.models.domain.event import Event
from app.models.domain.user import User
from app.models.schemas.event import EventsFilter, EventResponse, EventsResponse, EventCreate, EventUpdate
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK, name="comments:create-comment")
async def create_event(
        request: EventCreate,
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
) -> WrapperResponse:
    if await event_repository.get_event_by_title(request.title):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.EVENT_IS_EXISTS)

    event = await event_repository.create_event_by_user_id(user.id, **request.__dict__)
    if not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.EVENT_CREATE_ERROR)

    return WrapperResponse(
        payload=EventResponse(
            event=Event(id=event.id, title=event.title)
        )
    )
