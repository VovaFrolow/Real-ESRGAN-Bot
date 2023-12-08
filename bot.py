import telebot
from process_image import process_image
from pysondb import db
import json


DEFAULT_MODE = "x2"


class DataBase:
    admins = {}

    def __init__(self):
        self.users = db.getDb("users_db.json")

    def get_user(self, chat_id):
        user = self.users.getByQuery({"chat_id": chat_id})
        if user is not None and user != []:
            return user[0]

        user = {
            "chat_id": chat_id,
            "mode": DEFAULT_MODE
        }
        self.users.add(user)
        return user

    def set_user(self, chat_id, mode):
        self.get_user(chat_id)   # Создаём пользователя, если его нет
        updated_user = {
            "chat_id": chat_id,
            "mode": mode
        }
        self.users.updateByQuery({"chat_id": chat_id}, updated_user)

    def del_user(self, id):
        self.users.deleteById(id)


class Bot:
    @staticmethod
    def get_keyboard_from_list(options):
        keyboard = telebot.types.InlineKeyboardMarkup()
        for option in options:
            key = telebot.types.InlineKeyboardButton(
                text=option, callback_data=option)
            keyboard.add(key)
        return keyboard

    def __init__(self, db):
        self.TG_API_TOKEN = None
        self.bot = None
        self.db = db

        with open(f'token.txt', 'r') as token_file:
            self.TG_API_TOKEN = token_file.read()
        try:
            self.bot = telebot.TeleBot(self.TG_API_TOKEN)
        except Exception as e:
            print(f'TG API TOKEN is incorrect: {e}')
            exit()

        @self.bot.message_handler(commands=['start'])
        def _handle_start_command(msg):
            message = 'Привет, это Real-ESRGAN Бот, осуществляющий увеличение разрешения входного изображения. ' \
                'Для того, чтобы воспользоваться этой функцией, просто отправьте сообщением изображение ' \
                'и немного подождите. Если хотите изменить коэффициент увеличения, то можете выбрать из доступных. '\
                'Стандартный коэффициент равен 2.'

            keyboard = Bot.get_keyboard_from_list(['x2', 'x4', 'x8'])
            self.bot.send_message(
                msg.from_user.id, text=message, reply_markup=keyboard
            )

        @self.bot.message_handler(content_types=['photo'])
        def photo(message):
            current_user = self.db.get_user(message.chat.id)
            fileID = message.photo[-1].file_id
            file_info = self.bot.get_file(fileID)
            downloaded_file = self.bot.download_file(file_info.file_path)
            with open("image.jpg", 'wb') as new_file:
                new_file.write(downloaded_file)

            try:
                result_path = process_image("image.jpg", current_user['mode'])
                with open(result_path, 'rb') as img:
                    self.bot.send_photo(message.from_user.id, img)
            except Exception as e:
                print(e)
                self.bot.send_message(message.chat.id, e)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            if call.data in ["x2", "x4", "x8"]:
                scale_mode = int(call.data.replace('x', ''))
                self.db.set_user(call.message.chat.id, scale_mode)
                self.bot.send_message(
                    call.message.chat.id, f'Выбран режим {call.data}'
                )
            else:
                self.bot.send_message(call.message.chat.id, "Неверная кнопка")

        @self.bot.message_handler(func=lambda _: True)
        def _get_text_init_messages(message):
            self.bot.send_message(message.from_user.id, 'Type /start')

    def start(self):
        while True:
            try:
                self.bot.polling(none_stop=True, interval=0)
            except Exception as e:
                print(e)


def main() -> None:
    db = DataBase()
    bot = Bot(db=db)
    bot.start()


if __name__ == "__main__":
    main()
