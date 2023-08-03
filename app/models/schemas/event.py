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
from typing import List
from pydantic import Field, HttpUrl

from app.models.common import BaseAppModel
from app.models.domain.event import Event
from app.models.domain.location import Location

DEFAULT_EVENTS_LIMIT = 100
DEFAULT_EVENTS_OFFSET = 0


class EventsFilter(BaseAppModel):
    limit: int = Field(DEFAULT_EVENTS_LIMIT, ge=1)
    offset: int = Field(DEFAULT_EVENTS_OFFSET, ge=0)


class EventResponse(BaseAppModel):
    event: Event


class EventsResponse(BaseAppModel):
    events: List[Event]


class EventCreate(BaseAppModel):
    title: str
    subtitle: str = ""
    text: str
    picture: HttpUrl
    location: Location
    start_at: datetime


class EventUpdate(BaseAppModel):
    title: str | None = None
    subtitle: str | None = None
    text: str | None = None
    picture: HttpUrl | None = None
    location: Location | None = None
    start_at: datetime | None = None
