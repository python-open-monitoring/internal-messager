import datetime
import os

import aiohttp
import aiormq.types
import jinja2
import ujson
from mailjet_rest import Client
from pydantic import ValidationError
from simple_print.functions import sprint

from database import methods as db_methods
from producer import methods as producer_methods
from settings import DEBUG
from settings import MAILJET_API_KEY
from settings import MAILJET_API_SECRET
from settings import PROJECT_MAIL
from settings import TELEGRAM_BOT_TOKEN

file_path = os.path.dirname(os.path.abspath(__file__))


class Mailer:
    def __init__(self, sender: str, recipient_list: list, subject: str = "", letter_body: str = "", mail_service: str = "mailjet", **kwargs):
        self.sender = sender
        self.recipient_list = recipient_list
        self.subject = subject
        self.letter_body = letter_body
        self.mail_service = mail_service
        self.kwargs = kwargs
        self.outcoming_mail: str = ""

    def send_email(self):
        self._template_render()
        if self.mail_service == "mailjet":
            self._send_mailjet()

    def _template_render(self):
        templateLoader = jinja2.FileSystemLoader(searchpath=f"{file_path}/mailer")
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template("mail_template.html")
        self.outcoming_mail = template.render(subject=self.subject, letter_body=self.letter_body)

    def _send_mailjet(self):
        api_key = MAILJET_API_KEY
        api_secret = MAILJET_API_SECRET
        mailjet = Client(auth=(api_key, api_secret), version="v3.1")
        data = {
            "Messages": [
                {
                    "From": {
                        "Email": f"{self.sender}",
                    },
                    "To": [
                        {
                            "Email": f"{self.recipient_list}",
                        }
                    ],
                    "Subject": f"{self.subject}",
                    "HTMLPart": f"{self.outcoming_mail}",
                }
            ]
        }
        mailjet.send.create(data=data)


class Messager:
    def __init__(self, data):
        self.data = data

    async def process_request(self):
        sprint(f"Messager :: process_request {self.data}", c="green", s=1, p=1)
        if self.data.get("message_type") == "monitor":
            await self._handle_monitor()
        return True

    async def _handle_monitor(self):
        sprint(f"Messager :: _handle_monitor {self.data}", c="cyan", s=1, p=1)
        user = await db_methods.get_user_by_monitor_id(self.data["monitor_id"])
        if user:
            if self.data["monitor_connection_establish"] == 1:
                await self._send_to_socket(user, self.data)
                # success_message_header = f"Monitor {self.data['monitor_name']} is up."
                # success_message_text = f"Хост {self.data['monitor_host']}. Порт {self.data['monitor_port']}."
                # await self._send_to_telegram(user["telegram_chat_id"], message_text=f"{success_message_header} \n{success_message_text}")
                # await self._send_to_email(user["email"], message_header=error_message_header, message_text=error_message_text)

            else:
                error_message_header = f"Monitor {self.data['monitor_name']} is down."
                error_message_text = f"Host {self.data['monitor_host']}. Port {self.data['monitor_port']}."
                await self._send_to_socket(user, self.data)
                await self._send_to_telegram(user["telegram_chat_id"], message_text=f"{error_message_header} \n{error_message_text}")
                # await self._send_to_email(user["email"], message_header=error_message_header, message_text=error_message_text)

    async def _send_to_socket(self, user, data):
        sprint(f"Messager :: _send_to_socket user={user} data={data}", c="cyan", s=1, p=1)
        data.update({"user_id": user["id"]})
        await producer_methods.external_gate__monitor_stat(data)

    async def _send_to_telegram(self, telegram_chat_id, message_text=None):
        sprint(f"Messager :: _send_to_telegram telegram_chat_id={telegram_chat_id} message_text={message_text}", c="cyan", s=1, p=1)
        telegram_api_url = "https://api.telegram.org/bot%s/sendMessage" % TELEGRAM_BOT_TOKEN
        data = {"chat_id": telegram_chat_id, "text": message_text}
        async with aiohttp.ClientSession() as session:
            async with session.post(telegram_api_url, json=data) as resp:
                pass

    async def _send_to_email(self, email, message_header=None, message_text=None):
        mailer_message = Mailer(sender=PROJECT_MAIL, recipient_list=(f"{email}"), subject=message_header, letter_body=message_text)
        mailer_message.send_email()


def validate_request_schema(request_schema):
    def wrap(func):
        async def wrapped(message: aiormq.types.DeliveredMessage):
            now = datetime.datetime.now().time()
            await message.channel.basic_ack(message.delivery.delivery_tag)
            sprint(f"{func.__name__} :: basic_ack [OK] :: {now}", c="green", s=1, p=1)

            json_rq = None
            request = None
            response = None
            error = None

            try:
                json_rq = ujson.loads(message.body)
                request = request_schema.validate(json_rq).dict()
            except ValidationError as error_message:
                error = f"ERROR REQUEST, VALIDATION ERROR: body={message.body} error={error_message}"
            except Exception as error_message:
                error = f"ERROR REQUEST: body={message.body} error={error_message}"

            if not error:
                sprint(f"{func.__name__} :: Request {json_rq}", c="yellow", s=1, p=1)
                try:
                    await func(request)
                except Exception as error_message:
                    error = f"ERROR RESPONSE: body={message.body} error={error_message}"

            if DEBUG:
                if error:
                    sprint(error, c="red", s=1, p=1)
                else:
                    sprint(f"{func.__name__} :: complete [OK]", c="green", s=1, p=1)

        return wrapped

    return wrap
