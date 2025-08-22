import re
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from config import MONTHS, WEEKDAYS
from re import search


async def parse_text_in_date(text: str):
    result_date = datetime.now()
    text = text.strip().lower()
    result_time = None
    dd_mm_yyyy = await _parse_dd_mm_yyy(text)

    if dd_mm_yyyy:
        return dd_mm_yyyy

    if ' в ' in text:
        result_time = await _parse_time(text) or time(hour=9, minute=0)

    if 'чере' in text:
        try:
            result_date = await _parse_in_an_time(text, result_date)
        except Exception as e:
            print('Ошибка в через')

    if 'завтра' in text:
        result_date = (result_date + timedelta(days=1))

    if 'послезавтра' in text:
        result_date = (result_date + timedelta(days=2))

    for key, value in MONTHS.items():
        if key in text:
            current_month = result_date.month
            if value >= current_month:
                result_month = value - current_month
            else:
                result_month = (12 - current_month) + value
            result_date = result_date + relativedelta(months=result_month)

    for key, value in WEEKDAYS.items():
        if key in text:
            delta_days = (value - result_date.weekday()) % 7
            if delta_days == 0:
                result_date = result_date
            else:
                result_date = result_date + timedelta(days=delta_days)

    if result_time:
        return datetime.combine(result_date, result_time)
    return result_date


async def _parse_in_an_time(text: str, result_date: datetime):
    if 'день' in text or 'дня' in text or 'дней' in text:
        number = search(r'через\s+(\d+)\s*(день|дня|дней)', text)
        try:
            result_date = (result_date + timedelta(days=int(number.group(1))))
        except AttributeError:
            result_date = (result_date + timedelta(days=1))

    if 'недел' in text:
        numbers = search(r'через\s+(\d+)\s*(неделю|недели|недель)', text)
        try:
            result_date = (result_date + timedelta(weeks=int(numbers.group(1))))
        except AttributeError:
            result_date = (result_date + timedelta(weeks=1))

    if 'месяц' in text:
        numbers = search(r'через\s+(\d+)\s*(месяц|месяца|месяцев)', text)
        try:
            result_date = (result_date + relativedelta(months=int(numbers.group(1))))
        except AttributeError:
            result_date = (result_date + relativedelta(months=1))

    if 'год' in text:
        numbers = search(r'\s+(\d+)\s*(год|года|лет)', text)
        try:
            result_date = (result_date + relativedelta(years=int(numbers.group(1))))
        except AttributeError:
            result_date = (result_date + relativedelta(years=1))

    if 'час' in text:
        numbers = search(r'через\s+(\d+)\s*(час|часа|часов)', text)
        try:
            result_date = (result_date + timedelta(hours=int(numbers.group(1))))
        except AttributeError:
            result_date = (result_date + timedelta(hours=1))

    if 'минут' in text:
        numbers = search(r'через\s+(\d+)\s*(минут|минуты|минуту)', text)
        try:
            result_date = (result_date + timedelta(minutes=int(numbers.group(1))))
        except AttributeError:
            result_date = (result_date + timedelta(minutes=1))

    if 'секунд' in text:
        numbers = search(r'через\s+(\d+)\s*(секунд|секунды|секунду)', text)
        try:
            result_date = (result_date + timedelta(seconds=int(numbers.group())))
        except AttributeError:
            result_date = (result_date + timedelta(seconds=1))
    return result_date


async def _parse_time(text: str):
    times = search(r'(?:\bв\s+|\bво\s+)(\d{1,2})[:.,]?(\d{0,2})', text)
    if times:
        hour = int(times.group(1))
        minute = int(times.group(2)) if times.group(2) else 0
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour, minute)
        if minute > 59:
            hour += minute // 60
            minute = minute % 60
            if hour >= 24:
                return None
            return time(hour, minute, second=0)
    return None


async def _parse_dd_mm_yyy(text: str):
    pattern = r'\b(\d{2})\.(\d{2})\.(\d{4})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})\b'
    parsed = search(pattern, text)
    if parsed:
        day = parsed.group(1)
        if int(day) > 31 or int(day) < 1:
            return False
        month = parsed.group(2)
        if int(month) > 12 or int(month) < 1:
            return False
        year = parsed.group(3)
        if int(year) < datetime.now().year or int(year) > 9999:
            return False
        hour = parsed.group(4)
        if int(hour) < 0 or int(hour) > 23:
            return False
        minute = parsed.group(5)
        if int(minute) < 0 or int(minute) > 59:
            return False
        second = parsed.group(6)
        if int(second) < 1 or int(second) > 59:
            return False
        return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    else:
        return False


async def parse_time_zone(text: str):
    timezone = search(r'^[+-]\d{1,2}[:.]\d{2}$', text.strip())
    if not timezone:
        return False
    else:
        sign = text[0]
        hours = int(re.split(r'[:.]', text[1:])[0])
        minutes = int(re.split(r'[:.]', text[1:])[1])

        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            return False

        total_minutes = hours * 60 + minutes

        return total_minutes if sign == '+' else -total_minutes




