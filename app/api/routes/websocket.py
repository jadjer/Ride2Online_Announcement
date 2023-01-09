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

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, FastAPI, BackgroundTasks
from starlette.responses import HTMLResponse

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.connection_manager import get_connection_manager
from app.api.dependencies.rabbitmq_client import get_rabbitmq_client
from app.connection_manager.connection_manager import ConnectionManager
from app.models.domain.action import Action, ActionType
from app.models.domain.user import User
from app.rabbitmq_client.rabbitmq_client import RabbitmqClient

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("")
async def get():
    return HTMLResponse(html)


@router.websocket("")
async def websocket_events(
        websocket: WebSocket,
        backgroun_tasks: BackgroundTasks
) -> None:
    app: FastAPI = websocket.app

    rabbitmq_client: RabbitmqClient = app.state.rabbitmq_client
    connection_manager: ConnectionManager = app.state.connection_manager

    def send_message_to_websocket():
        while True:
            action = rabbitmq_client.get_action()
            print(action)
            if action:
                connection_manager.send_personal_message(action.json(), websocket)

    backgroun_tasks.add_task(send_message_to_websocket)

    await connection_manager.connect(websocket)
    rabbitmq_client.set_action(Action(type=ActionType.EVENT_USER_ONLINE))

    try:
        while True:
            data = await websocket.receive_text()

            await connection_manager.send_personal_message(f"You wrote: {data}", websocket)
            await connection_manager.broadcast(f"Client says: {data}")

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast(f"Client left the chat")
        rabbitmq_client.set_action(Action(type=ActionType.EVENT_USER_ONLINE))
