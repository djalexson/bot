import telebot
import os
import glob
from telebot import types

# Токен вашего Telegram-бота
bot_token = 'токен бота для комментариев'

# Путь к директории с txt-файлами
directory = 'куда парсер сохраняет файлы'

# Имя файла, в который будут сохраняться сообщения
file_name = 'chat_history.txt'

# Создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# Словарь для хранения последнего отправленного ответа для каждого пользователя
last_responses = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Бот запущен. Все сообщения будут сохраняться.')

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def save_message(message):
    chat_id = message.chat.id
    message_text = message.text

    with open(file_name, 'a', encoding='ANSI') as file:
        file.write(f'\n{message_text}')

    # Чтение файла и построчный анализ
    with open(file_name, 'r', encoding='ANSI') as file:
        last_line = None  # Переменная для хранения последней строки
        for line in file:
            last_line = line.rstrip('\n')

        # Проверка, был ли уже отправлен ответ пользователю
        if chat_id in last_responses:
            return

        # Перебор файлов в директории
        for filename in os.listdir(directory):
            if filename.endswith('.txt') and filename != file_name:
                file_path = os.path.join(directory, filename)

                # Чтение файла и построчный анализ
                with open(file_path, 'r', encoding='ANSI') as search_file:
                    for search_line in search_file:
                        search_line = search_line.rstrip('\n')

                        # Проверка наличия целевой строки в строке файла
                        if last_line in search_line:
                            parts = filename.split('.')
                            if len(parts) < 2:
                                continue

                            dynamic_numbers = parts[0]
                            response_file_pattern = f'{dynamic_numbers}.*.txt'
                            response_file_paths = glob.glob(os.path.join(directory, response_file_pattern))
                            if response_file_paths:
                                for response_file_path in response_file_paths:
                                    response_parts = os.path.basename(response_file_path).split('.')
                                    if len(response_parts) < 3:
                                        continue

                                    response_message_number = response_parts[0]
                                    response_index = response_parts[1]
                                    if response_message_number != dynamic_numbers or response_index == '1':
                                        continue

                                    with open(response_file_path, 'r', encoding='ANSI') as response_file:
                                        response_line = response_file.readline().rstrip('\n')

                                    response_line = response_line.replace('#NUMBERS#', dynamic_numbers)
                                    bot.reply_to(message, response_line)

                                    

                                    # Отправка фотографий в ответ на сообщения
                                    send_photos(chat_id, dynamic_numbers, response_index)

                                    # Добавление информации о последнем отправленном ответе
                                    last_responses[chat_id] = True

# Функция отправки фотографий
def send_photos(chat_id, dynamic_numbers, response_index):
    
    while True:
        
        photo_path = os.path.join(directory, f'{dynamic_numbers}.2.1.jpg')
        if not os.path.exists(photo_path):
            break

        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)

        response_index += 1

# Запуск бота
bot.infinity_polling()
