from aiogram import Bot, Dispatcher, types
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tauth.views import is_user, register
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from tauth.models import TelegramUser
from aiogram.utils import executor
from django.core.management.base import BaseCommand
from django.conf import settings

kb_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                              keyboard=[
                                  [
                                      KeyboardButton(text='/register')
                                  ],
                                  [
                                      KeyboardButton(text='Go to site')
                                  ]
                              ]
                              )


class PasswordState(StatesGroup):
    password1 = State()
    password2 = State()


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        bot = Bot(token=settings.TOKEN)
        dp = Dispatcher(bot, storage=MemoryStorage())

        @dp.message_handler(commands=['menu'])
        async def menu(message: types.Message):
            await message.answer('Wellcome to site-registration', reply_markup=kb_menu)

        @dp.message_handler(commands=['start'])
        async def get_massage(message: types.Message):
            await menu(message)
            chat_id = message.chat.id
            username = message.from_user.username.lower()
            user_id = message.from_user.id
            name = message.from_user.first_name
            link = message.from_user.url

            if not (await is_user(username)):

                @dp.message_handler(commands=['register'])
                async def get_pass(message: types.Message):
                    key = ReplyKeyboardMarkup(
                        keyboard=[
                            [
                                KeyboardButton(text='Cancel registration')
                            ],
                        ],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await message.answer('Enter password:', reply_markup=key)
                    await PasswordState.password1.set()

                @dp.message_handler(state=PasswordState.password1)
                async def process_pas1(message: types.Message, state: FSMContext):
                    if '@' and '/' and ' ' not in message.text and len(message.text) >= 8:
                        await state.update_data(password1=message.text)
                        # data = await state.get_data()
                        # p1 = data.get('password1')
                        # print(p1)
                        conf = ReplyKeyboardMarkup(
                            keyboard=[
                                [
                                    KeyboardButton(text='Cancel registration')
                                ],
                            ],
                            resize_keyboard=True,
                            one_time_keyboard=True
                        )
                        await message.answer('Confirm password', reply_markup=conf)
                        await PasswordState.password2.set()
                    else:
                        await message.answer('Password must have minimum 8 simbols and not contains special symbols ')

                    @dp.message_handler(state=PasswordState.password2)
                    async def process_pas2(message: types.Message, state: FSMContext):
                        await state.update_data(password2=message.text)
                        if '@' and '/' and ' ' not in message.text and len(message.text) >= 8:
                            await state.update_data(password2=message.text)
                            # data = await state.get_data()
                            # p1 = data.get('password1')
                            # print(p1)
                            conf = ReplyKeyboardMarkup(
                                keyboard=[
                                    [
                                        KeyboardButton(text='Cancel registration')
                                    ],
                                ],
                                resize_keyboard=True,
                                one_time_keyboard=True
                            )

                            data = await state.get_data()
                            p1 = data.get('password1')
                            p2 = data.get('password2')
                            print(p1, p2)

                            if p2 != p1:
                                await message.answer(
                                    'Passwords must be the same ')

                            else:
                                await register(username=username, password=p2, name=name, user_id=user_id, link=link)

                                await bot.send_message(chat_id=chat_id, text='Registration successful',
                                                       reply_markup=kb_menu)

                        else:
                            await message.answer(
                                'Password must have minimum 8 simbols and not contains special symbols ')

            else:
                await bot.send_message(chat_id=chat_id,
                                       text=f'User already registered \nYour current username to login: \n{username}')

        executor.start_polling(dp)
