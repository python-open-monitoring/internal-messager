from .helpers import Messager


async def monitor(incoming_data):
    incoming_data.update({"message_type": "monitor"})
    messager = Messager(data=incoming_data)
    await messager.process_request()
