import aiormq
from simple_print import sprint

from consumer import handlers
from settings import AMQP_URI


async def consumer_subscriptions():
    connection = await aiormq.connect(AMQP_URI)
    channel = await connection.channel()
    sprint("AMQP CONSUMER:     ready [yes]", c="green", s=1, p=1)

    monitor__declared = await channel.queue_declare("monitoring:internal__messager:monitor")
    await channel.basic_consume(monitor__declared.queue, handlers.monitor)
