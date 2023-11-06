import asyncio
import json
from asyncio import AbstractEventLoop
from functools import partial
from typing import NoReturn

import aiofiles
import ijson
from aio_pika import connect, Message
from aio_pika.abc import AbstractIncomingMessage, DeliveryMode

from config import DATA_PATH, RABBIT_LOGIN, RABBIT_PASS, RABBIT_HOST
from report_maker import ReportMaker, logger


class ReportMakingService:

    def __init__(self, loop: AbstractEventLoop):
        self.loop = loop
        self.DATA = []

    async def on_message(self, message: AbstractIncomingMessage, data: list[dict]) -> NoReturn:
        async with message.process():
            logger.info(f"Message body is: {message.body!r}")
            for task in json.loads(message.body):
                report_maker = ReportMaker(data, task)
                task = self.loop.create_task(report_maker.make_report())
                await self.publish_message_with_task_done(await task)

    @staticmethod
    async def publish_message_with_task_done(task: dict) -> NoReturn:
        queue_name = "tasks_done"
        async with await connect(f"amqp://{RABBIT_LOGIN}:{RABBIT_PASS}@{RABBIT_HOST}/") as connection:
            channel = await connection.channel()

            await channel.set_qos(prefetch_count=1)

            await channel.declare_queue(queue_name)
            message = Message(
                json.dumps(task, indent=4).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT,
            )
            await channel.default_exchange.publish(
                message,
                routing_key=queue_name,
            )

    async def main(self) -> NoReturn:
        async with aiofiles.open(DATA_PATH, "rb") as f:
            async for call_data in ijson.items(f, 'item'):
                self.DATA.append(call_data)
        async with await connect(f"amqp://{RABBIT_LOGIN}:{RABBIT_PASS}@{RABBIT_HOST}/") as connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)

            queue = await channel.declare_queue(
                "tasks",
                durable=True,
            )

            await queue.consume(partial(self.on_message, data=self.DATA))

            logger.info(" [*] Waiting for messages. To exit press CTRL+C")
            await asyncio.Future()
