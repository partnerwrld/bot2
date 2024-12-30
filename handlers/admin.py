from aiogram import F, Router, types, Bot
from aiogram.filters.command import CommandStart
from keyboards.admin import admin_command
from database.db import DataBase
from aiogram.fsm.context import FSMContext
from database.db import DataBase
from config import ADMIN_ID
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
class Admin_States(StatesGroup):

    get_userinfo = State()
    give_balance = State()
    

    get_userinfo_del = State()
    delete_balance = State()


    mailing_type = State()
    mailing_text = State()
   

router = Router()

@router.message(F.text == '/admin')
async def admin_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await state.clear()
        users_count = await DataBase.get_users()
        money_list = await DataBase.get_users()
        money_count = 0

        await message.answer("Добро пожаловать", reply_markup=await admin_command(), parse_mode="HTML")



@router.callback_query(F.data == 'stat')
async def statistics_handler(callback: types.CallbackQuery):
    # Получаем количество пользователей
    users_count = await DataBase.get_users_count()
    
    # Формируем сообщение со статистикой
    statistics_message = (
        f"<b>📊 Статистика бота:</b>\n\n"
        f"👥 <b>Общее количество пользователей:</b> <code>{users_count}</code>\n"
    )

    # Отправляем сообщение пользователю
    await callback.message.answer(statistics_message, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'mailing')
async def mailing_state(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Отправьте сообщение")
    await state.set_state(Admin_States.mailing_text)


@router.message(Admin_States.mailing_text)
async def mailing_state(message: types.Message, state: FSMContext, bot: Bot):
    mailing_message = message.message_id
    ikb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Отправить', callback_data='send_mailing'), types.InlineKeyboardButton(
            text='Отмена', callback_data='decline_mailing')]
    ])
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id,
                           message_id=mailing_message, reply_markup=ikb, parse_mode="HTML")

    await state.update_data(msg=mailing_message)


@router.callback_query(F.data == 'send_mailing')
async def mailing_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    errors_count = 0
    good_count = 0
    data = await state.get_data()
    mailing_message = data['msg']
    users = await DataBase.get_users()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Рассылка начата...")
    for i in users:
        try:
            await bot.copy_message(chat_id=i[1], from_chat_id=callback.from_user.id,
                                   message_id=mailing_message, parse_mode="HTML")
            good_count += 1
        except Exception as ex:
            errors_count += 1
            print(ex)

    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(f"<b>Кол-во отосланных сообщений:</b> <code>{good_count}</code>\n\
<b>Кол-во пользователей заблокировавших бота:</b> <code>{errors_count}</code>", parse_mode="HTML")
    await callback.answer()
    await state.clear()


@router.callback_query(F.data == 'decline_mailing')
async def decline_mailing(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Рассылка отменена", reply_markup=await admin_command())
    await state.clear()



@router.callback_query(F.data == "change_ref")
async def change_ref_handler(callback: types.CallbackQuery):
    current_ref = await DataBase.get_ref()
    message_text = (
        f"<b>Текущая реферальная ссылка:</b> <code>{current_ref}</code>\n\n"
        f"Для изменения отправьте новую ссылку в формате:\n"
        f"<code>/set_ref новая_ссылка</code>"
    )
    await callback.message.answer(message_text, parse_mode="HTML")
    await callback.answer()

@router.message(lambda message: message.text.startswith('/set_ref'))
async def set_ref_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    try:
        new_ref = message.text.split()[1]
        await DataBase.edit_ref(new_ref)
        await message.answer(f"✅ Реферальная ссылка успешно изменена на: <code>{new_ref}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer("❌ Ошибка при изменении ссылки. Проверьте формат команды:\n/set_ref новая_ссылка")

@router.callback_query(F.data == "change_ref")
async def change_ref_handler(callback: types.CallbackQuery):
    current_ref = await DataBase.get_ref()
    message_text = (
        f"<b>Текущая реферальная ссылка:</b> <code>{current_ref}</code>\n\n"
        f"Для изменения отправьте новую ссылку в формате:\n"
        f"<code>/set_ref новая_ссылка</code>"
    )