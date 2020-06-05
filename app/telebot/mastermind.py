import telegram
from app.telebot.credentials import bot_token, bot_user_name

ip = '178.63.41.235'
port = '9999'


global bot
TOKEN = bot_token
CHAT_ID = -386221977
pp = telegram.utils.request.Request(proxy_url='socks5h://{}:{}'.format(ip, port))
bot = telegram.Bot(token=TOKEN, request=pp)

def send_message(text):
    bot.sendMessage(chat_id=CHAT_ID, text=text)
