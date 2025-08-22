from aiogram.fsm.state import State, StatesGroup


class ReminderStates(StatesGroup):
    settings = State()
    timezone = State()
    messages = State()
    reminder_date = State()
    reminder_delete = State()

