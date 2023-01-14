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

from pydantic import BaseModel
from enum import Enum


class ActionType(Enum):
    EVENT_ADD = 0
    EVENT_UPDATE = 1
    EVENT_DELETE = 2
    EVENT_USER_ONLINE = 10
    EVENT_USER_OFFLINE = 11


class Action(BaseModel):
    type: ActionType
