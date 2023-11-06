import asyncio
import json
from typing import NoReturn

from aio_pika import connect, Message, DeliveryMode


tasks = [
    {
        "correlation_id": 13242421424214,
        "phones": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    },
    {
        "correlation_id": 13242421424215,
        "phones": [11, 12, 13, 14, 15, 16, 17, 18, 19]
    },
    {
        "correlation_id": 13242421424216,
        "phones": [21, 22, 23, 24, 25, 26]
    },
    {
        "correlation_id": 13242421424217,
        "phones": [31, 32, 33, 34, 35, 36, 37, 38, 39, 30]
    },
    {
        "correlation_id": 13242421424218,
        "phones": [41, 42, 43, 44]
    },
    {
        "correlation_id": 13242421424219,
        "phones": [51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
    },
    {
        "correlation_id": 13242421424220,
        "phones": [61, 62]
    },
    {
        "correlation_id": 13242421424221,
        "phones": [71, 72, 73, 74, 75, 76, 77, 78, 79, 80]
    },
    {
        "correlation_id": 13242421424222,
        "phones": [81, 82, 83, 88, 89, 90]
    },
]


async def publish_message_with_task_done(new_tasks: list[dict]) -> NoReturn:
    queue_name = "tasks"
    async with await connect("amqp://guest:guest@localhost/") as connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        message = Message(
            json.dumps(new_tasks, indent=4).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT,
            )
        await channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )

if __name__ == '__main__':
    asyncio.run(publish_message_with_task_done(tasks))
