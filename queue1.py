import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_message_to_telegram(chat_id, text, photo_url=None, caption=None):
    # Замените YOUR_TELEGRAM_BOT_TOKEN на ваш токен Telegram бота
    telegram_bot_token = "6149357251:AAGhxj-iCnP0jb-yMPUcSRPH-qJZ0aIyeFM"
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "photo": photo_url,
        "caption": caption
    }

    response = requests.post(telegram_api_url, json=payload)

    if response.status_code != 200:
        print("Не удалось отправить сообщение в Telegram.")
        print(response.json())

def send_photo_to_telegram(chat_id, photo_url, caption=None):
    # Замените YOUR_TELEGRAM_BOT_TOKEN на ваш токен Telegram бота
    telegram_bot_token = "токен бота"
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendPhoto"

    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption
    }

    response = requests.post(telegram_api_url, json=payload)

    if response.status_code != 200:
        print("Не удалось отправить фотографию в Telegram.")
        print(response.json())

def send_file_to_telegram(chat_id, file_path, file_name):
    # Замените YOUR_TELEGRAM_BOT_TOKEN на ваш токен Telegram бота
    telegram_bot_token = "токен бота"
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendDocument"

    with open(file_path, 'rb') as file:
        payload = {
            "chat_id": chat_id
        }
        files = {
            "document": file
        }

        response = requests.post(telegram_api_url, data=payload, files=files)

        if response.status_code != 200:
            print("Не удалось отправить файл в Telegram.")
            print(response.json())


def send_slack_message_to_telegram(slack_token, channel_id, telegram_chat_id):
    # Инициализация Slack WebClient
    client = WebClient(token=slack_token)

    try:
        # Запрашиваем список сообщений из Slack канала
        response = client.conversations_history(channel=channel_id)

        # Перебираем каждое сообщение и отправляем текстовые сообщения и файлы
        for message in reversed(response["messages"]):
            # Отправляем текстовое сообщение
            if "text" in message:
                text = message["text"]

                # Проверяем, есть ли фотография с текстом
                if "files" in message:
                    for file in message["files"]:
                        file_type = file.get("filetype")

                        # Обрабатываем только изображения
                        if file_type == "image":
                            photo_url = file.get("url_private")
                            caption = file.get("initial_comment", {}).get("comment")
                            send_message_to_telegram(telegram_chat_id, text, photo_url, caption)
                            break  # Прерываем цикл после отправки фотографии

                # Отправляем только текстовое сообщение
                send_message_to_telegram(telegram_chat_id, text)

            # Отправляем файлы, если они есть
            if "files" in message:
                for file in message["files"]:
                    file_url_private = file.get("url_private")
                    file_name = file.get("name")
                    download_and_send_file(file_url_private, telegram_chat_id, file_name)

    except SlackApiError as e:
        print(f"Произошла ошибка при запросе к Slack API: {e.response['error']}")


def download_and_send_file(file_url, chat_id, file_name):
    # Загрузка файла с Slack
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        # Создание пути и имени файла для сохранения
        save_path = os.path.join("files", file_name)

        # Сохранение файла локально
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        
        # Отправка файла в Telegram
        send_file_to_telegram(chat_id, save_path, file_name)

        # Удаление сохраненного файла
        os.remove(save_path)
    else:
        print("Не удалось загрузить файл с Slack.")


# Замените YOUR_SLACK_TOKEN на ваш токен Slack приложения
slack_token = "токен slack"

# Замените CHANNEL_ID на идентификатор Slack канала, из которого хотите отправлять сообщения в Telegram
channel_id = "id channel slack"

# Замените TELEGRAM_CHAT_ID на идентификатор Telegram чата или канала, в который будут отправляться сообщения
telegram_chat_id = "id tg chat"

# Создание папки для сохранения файлов, если ее не существует
if not os.path.exists("files"):
    os.makedirs("files")

# Отправляем сообщения и файлы из Slack в Telegram
send_slack_message_to_telegram(slack_token, channel_id, telegram_chat_id)
