from aiogram.dispatcher.filters.state import StatesGroup, State


class State(StatesGroup):
    changing_openai = State()
    changing_wb_ip = State()
    changing_wb_ooo = State()
    changing_group = State()
    changing_proxy = State()
    changing_instructions = State()
    changing_rec_instructions = State()
    choosing_automod = State()