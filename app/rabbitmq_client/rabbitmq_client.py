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

from pika import BlockingConnection, ConnectionParameters
from pika.credentials import PlainCredentials

from queue import Queue

from app.models.domain.action import Action


class RabbitmqClient(object):

    def __init__(self, host: str, port: int, user: str, password: str):
        self._connection = BlockingConnection(
            ConnectionParameters(
                host=host,
                port=port,
                credentials=PlainCredentials(
                    username=user,
                    password=password,
                ),
            )
        )

        self._queue = Queue()
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue="action")

    def start(self):
        self._channel.start_consuming()

    def stop(self):
        self._channel.stop_consuming()
        self._connection.close()

    def get_action(self) -> Action | None:
        _, _, data = self._channel.basic_get(queue="action", auto_ack=True)

        if not data:
            return None

        action_json = data.decode("utf-8")

        return Action.parse_raw(action_json)

    def set_action(self, action: Action):
        action_json: str = action.json()
        action_data: bytes = bytes(action_json, "utf-8")

        self._channel.basic_publish(exchange="", routing_key="action", body=action_data)
