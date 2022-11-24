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

from fastapi import APIRouter, Depends, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.get_from_path import get_event_id_from_path
from app.models.domain.user import User
from app.models.schemas.wrapper import WrapperResponse

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="events:get-events-by-filter")
async def get_events_by_filter(
        user: User = Depends(get_current_user_authorizer),
) -> WrapperResponse:
    return WrapperResponse()


@router.post("", status_code=status.HTTP_200_OK, name="events:create-event")
async def create_event(
        user: User = Depends(get_current_user_authorizer),
) -> WrapperResponse:
    return WrapperResponse()


@router.get("/{event_id}", status_code=status.HTTP_200_OK, name="events:get-event-by-id")
async def get_event_by_id(
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
) -> WrapperResponse:
    return WrapperResponse()


@router.patch('/{event_id}', status_code=status.HTTP_200_OK, name="events:update-event-by-id")
async def update_event_by_id(
        event_id: int = Depends(get_event_id_from_path),
        user: User = Depends(get_current_user_authorizer),
) -> WrapperResponse:
    return WrapperResponse()
