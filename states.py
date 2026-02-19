from aiogram.dispatcher.filters.state import StatesGroup, State


class State(StatesGroup):
    changing_openai = State()
    changing_ozon = State()
    changing_group = State()
    changing_proxy = State()
    changing_instructions = State()
    changing_rec_instructions = State()
    choosing_automod = State()