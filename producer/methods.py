import datetime
import json
from contextlib import asynccontextmanager

import aiormq
from simple_print import sprint

from settings import AMQP_URI


@asynccontextmanager
async def rabbitmq_get_channel():
    connection = await aiormq.connect(AMQP_URI)
    try:
        channel = await connection.channel()
        yield channel
    finally:
        await connection.close()


async def external_gate__monitor_stat(outcoming_data):
    time_now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    sprint(f"AMQP PRODUCER:     external_gate__monitor_stat time={time_now} data={outcoming_data}", с="green", s=1, p=1)
    outcoming_data_bytes = json.dumps(outcoming_data).encode()
    async with rabbitmq_get_channel() as channel:
        await channel.basic_publish(outcoming_data_bytes, routing_key=f"monitoring:external__gate:monitor_stat")
