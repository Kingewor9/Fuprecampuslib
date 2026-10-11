from aiogram.fsm.state import State, StatesGroup


class AdminUploadStates(StatesGroup):
    waiting_for_file = State()
    choosing_college = State()
    choosing_department = State()
    choosing_level = State()
    choosing_type = State()
    waiting_for_title = State()
    confirming = State()
