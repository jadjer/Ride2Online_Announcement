#  Copyright 2023 Pavel Suprunov
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
from app.api.dependencies.database import get_repository
from app.database.repositories.event_repository import EventRepository
from app.models.domain.location import Location
from app.models.domain.user import User
from app.models.schemas.wrapper import WrapperResponse

router = APIRouter()


@router.post("", status_code=status.HTTP_200_OK, name="vehicles-location:update-location")
async def update_location(
        request: Location,
        user: User = Depends(get_current_user_authorizer),
        event_repository: EventRepository = Depends(get_repository(EventRepository)),
) -> WrapperResponse:
    return WrapperResponse()
