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

from fastapi import Query

from app.models.schemas.event import DEFAULT_EVENTS_LIMIT, DEFAULT_EVENTS_OFFSET, EventsFilter


def get_events_filter(
        limit: int = Query(DEFAULT_EVENTS_LIMIT, ge=1),
        offset: int = Query(DEFAULT_EVENTS_OFFSET, ge=0),
) -> EventsFilter:
    return EventsFilter(limit=limit, offset=offset)
