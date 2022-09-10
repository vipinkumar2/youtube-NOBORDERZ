import discord,requests,os,random
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
load_dotenv()

client = discord.Client()

class TelegramUtilities:
    def __init__(self, bot_api_key):
        self.bot_api_key = bot_api_key

    def get_updates(self):

        url = f"https://api.telegram.org/bot{self.bot_api_key}/getUpdates"
        response = requests.get(url=url)
        print(response.json())
        if response.json().get('ok'):
            if response.json().get('result', None):
                chat_id = response.json().get('result', None)[0].get('message', None).get('chat', None).get('id', None)
                chat_type = response.json().get('result', None)[0].get('message', None).get('chat', None).get('type', None)
                title = response.json().get('result', None)[0].get('message', None).get('chat', None).get('title', None)

    def post_message(self, message, chat_id):
        user_data = {
            "text": message,
            "chat_id": chat_id
        }

        url = f"https://api.telegram.org/bot{self.bot_api_key}/sendMessage"
        response = requests.post(
            url=url, data=user_data
        )
        print(response.json())




@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if str(message.channel).endswith("announcements"):
        print(f'Transfer of announcement from {message.channel} channel to Telegram has been initiated')
        tlutili = TelegramUtilities(bot_api_key=os.getenv('TELEGRAM_BOT_API_KEY','1768483255:AAGsz6t_tk4_3ttcB12M60xIyf8s1QbR8iM'))
        tlutili.post_message(message.content, os.getenv('TELEGRAM_CHANNEL_ID',-1001343808067))
    else:
        print(f'Transferring messages from {message.channel} is restricted')


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        client.run(os.getenv('DISCORD_BOT_TOKEN', 'ODI3NTQ3NzU5MjIwNDkwMjgx.YGcn6A.2yd1EWlKswNGIt-SsXF7OJLeWsw'))


