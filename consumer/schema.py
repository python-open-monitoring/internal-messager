from pydantic import BaseModel


class Monitor(BaseModel):
    monitor_name: str
    monitor_id: int
    monitor_host: str
    monitor_port: str
    monitor_connection_establish: int
    monitor_request_time: str
    monitor_response_time: int
