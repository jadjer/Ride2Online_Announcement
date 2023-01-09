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

from fastapi import FastAPI
from loguru import logger

from app.core.settings.app import AppSettings
from .rabbitmq_client import RabbitmqClient


def start_rabbitmq_client(app: FastAPI, settings: AppSettings):
    logger.info("Connect to RabbitMQ")

    rabbitmq_client = RabbitmqClient(
        settings.rabbitmq_host,
        settings.rabbitmq_port,
        settings.rabbitmq_user,
        settings.rabbitmq_pass,
    )
    rabbitmq_client.start()

    app.state.rabbitmq_client = rabbitmq_client

    logger.info("Connection to RabbitMQ established")


def stop_rabbitmq_client(app: FastAPI) -> None:
    logger.info("Closing connection to RabbitMQ")

    rabbitmq_client: RabbitmqClient = app.state.rabbitmq_client
    rabbitmq_client.stop()

    logger.info("Connection closed")
