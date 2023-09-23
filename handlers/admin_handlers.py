from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, CallbackQuery

from bot_menu.menu import create_inline_kb
from database.orm import add_card_players, add_card_goalkeeper, get_user
from lexicon.lexicon_ru import MENU, PLAYERS

router: Router = Router()


'''FSM для добавления игрока - Нападающий и защитник'''
class FSMadd_player(StatesGroup):
    name = State()
    img = State()
    position = State()
    attack = State()
    endurance = State()
    power = State()
    defense = State()
    pur_price = State()
    sal_price = State()


'''FSM для добавления игрока - Вратарь'''
class FSMadd_goalkeeper(StatesGroup):
    name = State()
    img = State()
    reliability = State()
    endurance = State()
    defense = State()
    pur_price = State()
    sal_price = State()




'''Команда /admin'''
@router.message(F.text == '/admin')
async def check_admin(message: Message):
    user = await get_user(message.from_user.id)
    if user['admin']:
        await message.answer(text='Выбери действие', reply_markup=await admin_kb())


'''Выбор кого добавить'''

@router.message(F.text == MENU['add_player'])
async def choise_add_player(message: Message, state: FSMContext):
    await message.answer(text='❓Пожалуйста, уточните, какую позицию игрока вы хотели бы добавить?❓',
                         reply_markup=create_inline_kb(1, 'add_player_',
                                                        PLAYERS['forward'],
                                                        PLAYERS['defender'],
                                                        PLAYERS['goalkeeper']))


    # await state.set_state(FSMadd_player.name)


'''Просим добавить фотографию'''

@router.callback_query(F.data.startswith('add_player_'))
async def add_player(callback: CallbackQuery, state: FSMContext):
    if callback.data.split('_')[-1] == PLAYERS['forward'] or callback.data.split('_')[-1] == PLAYERS['defender']:
        await state.set_state(FSMadd_player.position)
        await state.update_data(position=callback.data.split('_')[-1])
        await state.set_state(FSMadd_player.name)
    else:
        await state.set_state(FSMadd_goalkeeper.name)
    await callback.message.answer(text='Введите имя игрока, для которого вы хотите создать карточку.')
    await callback.answer()



'''Ввод имени карточки нападающего или защитника'''

@router.message(StateFilter(FSMadd_player.name))
async def add_name_card(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Загрузите изображение игрока')
    await state.set_state(FSMadd_player.img)



'''Ввод изображения карточки нападающего или защитника'''

@router.message(StateFilter(FSMadd_player.img))
async def add_img_card(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(img=message.photo[-1].file_id)
        await message.answer(text='Введите параметр атаки игрока')
        await state.set_state(FSMadd_player.attack)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы отправляете не фотографию\n'
                                  'Попробуй заново')



'''Ввод параметра атаки карточки нападающего или защитника'''
@router.message(StateFilter(FSMadd_player.attack))
async def add_attack_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(attack=int(message.text))
        await message.answer(text='Введите параметр выносливости игрока')
        await state.set_state(FSMadd_player.endurance)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')



'''Ввод параметра выносливости карточки нападающего или защитника'''
@router.message(StateFilter(FSMadd_player.endurance))
async def add_endurance_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(endurance=int(message.text))
        await message.answer(text='Введите параметр силы игрока')
        await state.set_state(FSMadd_player.power)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Ввод параметра защиты карточки нападающего или защитника defense'''
@router.message(StateFilter(FSMadd_player.power))
async def add_endurance_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(power=int(message.text))
        await message.answer(text='Введите параметр защиты игрока')
        await state.set_state(FSMadd_player.defense)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')



'''Ввод параметра цены покупки карточки нападающего или защитника'''
@router.message(StateFilter(FSMadd_player.defense))
async def add_defense_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(defense=int(message.text))
        await message.answer(text='Введите цену покупки игрока')
        await state.set_state(FSMadd_player.pur_price)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')



'''Ввод параметра цены продажи карточки нападающего или защитника'''

@router.message(StateFilter(FSMadd_player.pur_price))
async def add_pur_price_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(pur_price=int(message.text))
        await message.answer(text='Введите цену продажи игрока')
        await state.set_state(FSMadd_player.sal_price)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')



'''Завершение добавления карточки нападающего или защитника'''
@router.message(StateFilter(FSMadd_player.sal_price))
async def add_sal_price_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(sal_price=int(message.text))
        new_card = await state.get_data()
        await add_card_players(new_card)
        await message.answer(text='✅Карточка успешно добавлена✅')
        await state.clear()
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Ввод имени карточки вратаря'''

@router.message(StateFilter(FSMadd_goalkeeper.name))
async def add_name_card(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Загрузите изображение игрока')
    await state.set_state(FSMadd_goalkeeper.img)



'''Ввод изображения карточки вратаря'''

@router.message(StateFilter(FSMadd_goalkeeper.img))
async def add_img_card(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(img=message.photo[-1].file_id)
        await message.answer(text='Введите параметр надежности игрока')
        await state.set_state(FSMadd_goalkeeper.reliability)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы отправляете не фотографию\n'
                                  'Попробуй заново')


'''Ввод параметра надежности карточки вратаря'''

@router.message(StateFilter(FSMadd_goalkeeper.reliability))
async def add_endurance_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(reliability=int(message.text))
        await message.answer(text='Введите параметр выносливости игрока')
        await state.set_state(FSMadd_goalkeeper.endurance)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Ввод параметра выносливости карточки вратаря'''

@router.message(StateFilter(FSMadd_goalkeeper.endurance))
async def add_endurance_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(endurance=int(message.text))
        await message.answer(text='Введите параметр защиты игрока')
        await state.set_state(FSMadd_goalkeeper.defense)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Ввод параметра цены покупки карточки вратаря'''
@router.message(StateFilter(FSMadd_goalkeeper.defense))
async def add_defense_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(defense=int(message.text))
        await message.answer(text='Введите цену покупки игрока')
        await state.set_state(FSMadd_goalkeeper.pur_price)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Ввод параметра цены продажи карточки вратаря'''

@router.message(StateFilter(FSMadd_goalkeeper.pur_price))
async def add_pur_price_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(pur_price=int(message.text))
        await message.answer(text='Введите цену продажи игрока')
        await state.set_state(FSMadd_goalkeeper.sal_price)
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Завершение добавления карточки вратаря'''
@router.message(StateFilter(FSMadd_goalkeeper.sal_price))
async def add_sal_price_card(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(sal_price=int(message.text))
        new_card = await state.get_data()
        await add_card_goalkeeper(new_card)
        await message.answer(text='✅Карточка успешно добавлена✅')
        await state.clear()
    else:
        await message.answer(text='❌Упс!\n'
                                  'Мне кажется вы ввели не число\n'
                                  'Попробуй заново')


'''Для отмены добавления'''

@router.message(F.text=='Отмена', StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text='Вы и не начинали добавлять')


@router.message(F.text=='Отмена', ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(text='Добавление отменено')
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()