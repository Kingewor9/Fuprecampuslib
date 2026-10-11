from aiogram.fsm.state import State, StatesGroup


class NavigationStates(StatesGroup):
    choosing_college = State()
    choosing_department = State()
    choosing_level = State()
    choosing_type = State()
    viewing_results = State()
