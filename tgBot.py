import telebot
from main import CheckToken, CheckAccountId, CheckPrice, StopProcess, GetBalance

bot = telebot.TeleBot("5264611634:AAG7PCOlAHxLc9-KHr_0rqDBOFbHBb2c05M")
TinkToken = ""
min, max = 0, 0
count = 0
Id = ""
cost = 0


@bot.message_handler(commands=['help', 'start'])
def send_help(message):
    bot.send_message(message.from_user.id, 'Воспользуйтесь /help, чтобы получить информацию о функциях\n'
                                           'Воспользуйтесь /reg, чтобы зарегистрировать свой токен\n'
                                           'Воспользуйтесь /process, чтобы приступить к торговле\n'
                                           'Воспользуйтесь /stop, чтобы завершить работа бота\n')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == '/reg':
        if message.text == '/stop':
            StopProcess()
            bot.send_message(message.from_user.id, 'Пока!')
            bot.stop_polling()
        bot.send_message(message.from_user.id, 'Введите токен для торговли в Тинькофф Инвестициях')
        bot.register_next_step_handler(message, save_token)

    if message.text == '/process':
        if message.text == '/stop':
            StopProcess()
            bot.send_message(message.from_user.id, 'Пока!')
            bot.stop_polling()

        if TinkToken == '':
            bot.send_message(message.from_user.id,
                             'Вы еще не зарегестрировались, введите токен для торговли в Тинькофф Инвестициях')
            bot.register_next_step_handler(message, save_token)
        else:
            bot.send_message(message.from_user.id, 'Начнем торговлю, введите минимум сетки')
            bot.register_next_step_handler(message, save_min)

    if message.text == '/stop':
        StopProcess()
        bot.send_message(message.from_user.id, 'Пока!')
        bot.stop_polling()

    # if message.text == '/balance':
    #     bot.register_next_step_handler(message, a)


def save_token(message):
    global TinkToken
    TinkToken = message.text

    if CheckToken(TinkToken):
        bot.send_message(message.from_user.id, 'Ваш токен верен вам!')
        bot.send_message(message.from_user.id, TinkToken)
        # нужна проверка на правильность токена с помощью попытки подключения к тиньку
        bot.send_message(message.from_user.id, 'Введите аккаунт айди для торговли в Тинькофф Инвестициях')
        bot.register_next_step_handler(message, save_account_id)
    else:
        bot.send_message(message.from_user.id, 'Твой токен полное дерьмо!')
        bot.register_next_step_handler(message, save_token)


def save_account_id(message):
    global Id
    global TinkToken
    Id = message.text

    if CheckAccountId(TinkToken, Id):
        bot.send_message(message.from_user.id, 'Ваш аккаунт айди верен вам!')
        bot.send_message(message.from_user.id, Id)
        bot.send_message(message.from_user.id, 'Воспользуйтесь /process, чтобы приступить к торговле')
        bot.register_next_step_handler(message, echo_all)
    else:
        bot.send_message(message.from_user.id, 'Твой аккаунт айди дерьмо!')
        bot.register_next_step_handler(message, save_account_id)


def save_min(message):
    global min
    global cost

    try:
        cost = CheckPrice(TinkToken)
        min = int(message.text)
        if cost < min:
            bot.send_message(message.from_user.id, 'Сетка не покрывает текущую стоимость, введите минимум снова:')
            min = 0
            bot.register_next_step_handler(message, save_min)

        # elif min <= 0:
        #     bot.send_message(message.from_user.id, 'Введено неположительное число. Попробуйте снова:')
        #     min = 0
        #     bot.register_next_step_handler(message, save_min)
        else:
            bot.send_message(message.from_user.id, 'Введите максимум сетки:')
            bot.register_next_step_handler(message, save_max)

    except Exception:
        bot.send_message(message.from_user.id, 'Введено не число. Попробуйте снова:')
        bot.register_next_step_handler(message, save_min)

    # if min > 0:
    #     bot.send_message(message.from_user.id, 'Введите максимум сетки:')
    #     bot.register_next_step_handler(message, save_max)


def save_max(message):
    global min
    global max
    global cost

    try:
        max = int(message.text)

        if max < cost:
            bot.send_message(message.from_user.id, 'Сетка не покрывает текущую стоимость, введите максимум снова:')
            max = 0
            bot.register_next_step_handler(message, save_max)

        elif max <= min:
            bot.send_message(message.from_user.id, 'Максимум сетки ⩽ минимума. Попробуйте снова, начиная с минимума:')
            max, min = 0, 0
            bot.register_next_step_handler(message, save_min)

        # elif max <= 0:
        #     bot.send_message(message.from_user.id, 'Введено неположительное число. Попробуйте снова:')
        #     max = 0
        #     bot.register_next_step_handler(message, save_max)

        if max > 0 and max > min and min > 0:
            bot.send_message(message.from_user.id, 'Минимум: ' + str(min) + '\nМаксимум: ' + str(max))
            bot.send_message(message.from_user.id, 'Введите количество делений сетки:')
            bot.register_next_step_handler(message, save_count)

    except Exception:
        bot.send_message(message.from_user.id, 'Введено не число. Попробуйте снова:')
        bot.register_next_step_handler(message, save_max)

    # if max > 0 and max > min and min > 0:
    #     bot.send_message(message.from_user.id, 'Минимум: ' + str(min) +'\nМаксимум: ' + str(max))
    #     bot.send_message(message.from_user.id, 'Введите количество делений сетки:')
    #     bot.register_next_step_handler(message, save_count)


def save_count(message):
    global count

    try:
        count = int(message.text)
        if count < 2:
            bot.send_message(message.from_user.id, 'Слишком малое число делений сетки. Попробуйте снова:')
            count = 0
            bot.register_next_step_handler(message, save_count)
    except Exception:
        bot.send_message(message.from_user.id, 'Введено не число. Попробуйте снова:')
        bot.register_next_step_handler(message, save_count)

    if count >= 2:
        bot.send_message(message.from_user.id, 'Количество делений сетки: ' + str(count))
        bot.send_message(message.from_user.id, 'Показать текущий баланс аккаунта? (yes/no)')
        bot.register_next_step_handler(message, check_balance)


def check_balance(message):
    if message.text.lower() == 'yes':
        balance = GetBalance(TinkToken, Id)
        bot.send_message(message.from_user.id, 'Ваш текущий баланс: ' + str(balance))

    bot.send_message(message.from_user.id, 'Запуск стратегии!')
    #main.StartAlgoBot(min, max, count, TinkToken, Id)
    bot.send_message(message.from_user.id, 'Показать текущий баланс аккаунта? (yes/no)')
    bot.register_next_step_handler(message, algo_process)


def algo_process(message):
    if message.text.lower() == 'yes':
        balance = GetBalance(TinkToken, Id)
        bot.send_message(message.from_user.id, 'Ваш текущий баланс: ' + str(balance))


bot.infinity_polling()
