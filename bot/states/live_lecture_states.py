from aiogram.fsm.state import State, StatesGroup


class LiveLectureStates(StatesGroup):
    choosing_college = State()
    choosing_department = State()