import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path + "/../")

import pprint
import pytest
from consumer.helpers import Messager


@pytest.mark.asyncio
async def test_messager():
    # pytest -s tests/test_messager.py
    incoming_data = {"monitor_id": "1", "monitor_name": "ya.ru", "monitor_host": "ya.ru", "monitor_port": 443, "monitor_connection_establish": 0, "monitor_response_time": 2, "_message_type": "monitor"}
    pprint.pprint(incoming_data)
    messager = Messager(incoming_data)
    result = await messager.process_request()
    assert result
