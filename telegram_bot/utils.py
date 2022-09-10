import requests
from telegram_bot.models import *
# from telegram.bot import Bot
# from telegram_bot.constants import API_KEYS


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
                # text = response.json().get('result', None)[0].get('message', None).get('text', None)
                if not Chats.objects.filter(chat_id=chat_id):
                    Chats.objects.create(chat_id=chat_id, type=chat_type, name=title)

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

    def post_photo(self, photo, chat_id):
        bot = Bot(self.bot_api_key)
        bot.send_photo(chat_id=chat_id, photo=photo)

    def setup_webhook(self, hook_url):
        url = f"https://api.telegram.org/bot{self.bot_api_key}/setWebhook?url={hook_url}"
        response = requests.post(
            url=url
        )
        print(response.json())


# obj = TelegramUtilities(bot_api_key=API_KEYS.get('linda2000_bot', None))
#
# # obj.get_updates()
# obj.post_photo(photo='https://twitter.com/xanalianft/status/1372068209122238464/photo/1',
#                chat_id=Chats.objects.filter(name='Xanalianft')[0].chat_id)
# obj.post_message(message="hello there", chat_id='1208778469')
# obj.post_on_channel(channel_username='bulls-n-bears', message="Today is blood bath in D-Street")
# obj.post_on_channel(channel_username='-1001439934687', message="Today is blood bath in D-Street")
# obj.setup_webhook(hook_url='https://4b8866548382.ngrok.io/telegram/setUpWebhook/')

"""
URL for setting Webhook

https://api.telegram.org/bot1774410287:AAGWWx1dm7B9kkCX_GSvP0NRt4SDbVOi6JM/setWebhook?url=https://20d30dc6e42c.ngrok.io/telegram/setUpWebhook/
"""
