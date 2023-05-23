import telebot
import requests
import json
from config import keys, TOKEN

#TOKEN = "6214650782:AAFVA745pv48-PMLieFWLtYVronDMPE7ucA"
bot = telebot.TeleBot(TOKEN)
bot.polling(none_stop=True)


class APIException(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def get_price(base: str, quote: str, amount: str):

        if quote == base:
            raise APIException(f'Введите различные валюты: {base}.')

        if quote in keys.values() or base in keys.values():
            raise APIException(f'Не удалось обработать валюту. Введите валюту в формате: евро, форинт, доллар, рубль. ')

        if int(amount) <= 0:
            raise APIException(f'Пожалуйста, введите сумму больше нуля.')

        # quote_ticker, base_ticker = keys[quote], keys[base]
        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {base}')
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Не удалось обработать валюту {quote}')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Не удалось обработать количество {amount}')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)[keys[base]]
        return total_base


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = 'Для начала работы введите команду в следующем формате (через пробел):' \
           ' \n- <Название валюты, которую Вы хотите поменять>  \n- <Название валюты, на которую Вы хотите поменять ' \
           'первую валюту> \n- <Количество первой валюты> \n Например, Вы хотите поменять 10 евро на доллары, то введите: евро доллар 10 \n \
 Список доступных валют: /currency'

    bot.reply_to(message, text)


@bot.message_handler(commands=['currency'])
def currency(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


# base, quote, amount = message.text.split(' ')
@bot.message_handler(content_types=['text', ])
def get_price(message: telebot.types.Message):
    try:
        values = message.text.split(' ')

        if len(values) != 3:
            raise APIException('Неверно введены параметры')

        base, quote, amount = values
        total_base = CryptoConverter.get_price(base, quote, amount)
        total = int(amount) / float(total_base)
        total = round(total, 2)

    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя. \n{e}')

    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка\n{e}')
    else:
        text = f'{amount} {base} в {quote}: {total}'
        bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)
