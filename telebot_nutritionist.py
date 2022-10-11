import recipies
import telebot
from telebot import types
import warnings
warnings.filterwarnings('ignore')

API_TOKEN = 'Токен (API ключ) который получили от BotFather'
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def start(m):
    # Добавляем две кнопки для 2х версий программы
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Forecast+Nutrients+Recipes")
    item2 = types.KeyboardButton("Daily menu")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(
        m.chat.id, 'Hi, I am smart nutritionist! '
        'Please choose and push: \nForecast+Nutrients+Recipes - '
        'if you want infromation about ingredients, which you have: '
        'forecast for that combination, nutritional value'
        'and relevant recipes\n'
        'Daily menu — if you want menu for a day',  reply_markup=markup)


# Получение сообщений от юзера
@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Если юзер прислал 1, то бот выдает меню на день
    if message.text.strip() == 'Daily menu':
        menu = recipies.Menu()
        answer1 = menu.breakfast()
        answer2 = menu.lunch()
        answer3 = menu.dinner()
        bot.send_message(message.chat.id, answer1)
        bot.send_message(message.chat.id, answer2)
        bot.send_message(message.chat.id, answer3)

    # Если юзер прислал 2, переходим на программу информации
    # для сочетания ингредиентов
    elif message.text.strip() == 'Forecast+Nutrients+Recipes':
        bot.send_message(message.chat.id,
                         "Please enter the list of ingredients "
                         "separated by commas")
        # следующий шаг – функция информации по ингредиентам
        bot.register_next_step_handler(
            message, get_ingredients)


def get_ingredients(message):
    request = message.text
    chat_id = message.chat.id
    # разобьём список на массив слов, используя split.
    list_of_ingredients = request.split(', ')

    res = recipies.Forecast(list_of_ingredients)
    res.preprocess()
    result1 = res.predict_rating_category()
    answer1 = "I. OUR FORECAST" + "\n" + result1
    nutr = recipies.NutritionFacts(list_of_ingredients)
    nutr.retrieve()
    result2 = nutr.filter()
    answer2 = "II. NUTRITIONAL VALUE" + "\n" + result2
    recip = recipies.SimilarRecipes(list_of_ingredients)
    recip.find_all()
    result3 = recip.top_similar()
    answer3 = "III. TOP-3 SIMILAR RECIPES" + "\n" + result3

    bot.send_message(chat_id, answer1)
    bot.send_message(chat_id, answer2)
    bot.send_message(chat_id, answer3)


# Запускаем бота
bot.polling(none_stop=True, interval=0)
