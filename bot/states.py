from aiogram.fsm.state import State, StatesGroup


class ChainStates(StatesGroup):
    choosing_f3 = State()
    choosing_f2 = State()
    choosing_f1 = State()
    waiting_x = State()
