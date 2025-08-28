from aiogram.fsm.state import State, StatesGroup


class ReminderStates(StatesGroup):
    settings = State()
    timezone = State()
    reminder_delete = State()
    date_messages = State()
    date_reminder_date = State()
    trigger_messages = State()
    trigger_reminder_date = State()


