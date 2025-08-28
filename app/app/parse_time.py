from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from config import MONTHS, WEEKDAYS
from logger_config import get_logger
from re import search, split
from pytz import FixedOffset
from apscheduler.triggers.cron import CronTrigger

logger = get_logger(__name__)


class ChangeText:
    def __init__(self, text=None):
        self.text = text

    def get_text(self):
        return self.text

    def update_text(self, text, pattern=None):
        parsed = search(pattern, self.text)
        self.text = self.text[:parsed.start() - 1] + text[parsed.end():]


change_text = ChangeText()


async def parse_text_in_date(text: str):
    result_date, current_date = datetime.now(), datetime.now()
    change_text.text = text.strip().lower()
    result_time = None
    dd_mm_yyyy = await _parse_dd_mm_yyy()
    hh_mm_ss = await _parse_time()

    if dd_mm_yyyy:
        return dd_mm_yyyy

    if hh_mm_ss:
        result_time = hh_mm_ss or time(hour=result_date.hour, minute=result_date.minute)

    try:

        if 'чере' in change_text.text:
            result_date = await _parse_in_an_time(result_date)

        if 'сегодня' in change_text.text:
            result_date = (result_date + timedelta(days=0))
            change_text.update_text(change_text.text, r'\bсегодня\b')
            logger.info(f'текст: {change_text.text}')

        if 'завтра' in change_text.text:
            result_date = (result_date + timedelta(days=1))
            change_text.update_text(change_text.text, r'\bзавтра\b')

        if 'послезавтра' in change_text.text:
            result_date = (result_date + timedelta(days=2))
            change_text.update_text(change_text.text, r'\bпослезавтра\b')

        for key, value in MONTHS.items():
            if key in text:
                current_month = result_date.month
                change_text.update_text(change_text.text, key)
                if value >= current_month:
                    result_month = value - current_month
                else:
                    result_month = (12 - current_month) + value
                result_date = result_date + relativedelta(months=result_month)

        for key, value in WEEKDAYS.items():
            if key in text:
                delta_days = (value - result_date.weekday()) % 7
                change_text.update_text(change_text.text, key)
                if delta_days == 0:
                    result_date = result_date
                else:
                    result_date = result_date + timedelta(days=delta_days)
        logger.info(f'Текст: {change_text.text}')
        result_date = await _parse_in_an_time(result_date)

        if result_time:
            return datetime.combine(result_date, result_time)

        if current_date != result_date:
            return result_date
        else:
            raise Exception('Не удалось распознать дату')
    except Exception as e:
        logger.error(f'При поиска даты в тексте произошла ошибка: {e}')
        raise Exception('Не удалось распознать дату')


async def _parse_in_an_time(result_date: datetime):
    if 'день' in change_text.text or 'дня' in change_text.text or 'дней' in change_text.text:
        pattern = r'через\s*(\d*)\s*(день|дня|дней)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + timedelta(days=1))
            else:
                result_date = (result_date + timedelta(days=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + timedelta(days=1))

    if 'недел' in change_text.text:
        pattern = r'через\s*(\d*)\s*(неделю|недели|недель|нед)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + timedelta(weeks=1))
            else:
                result_date = (result_date + timedelta(weeks=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + timedelta(weeks=1))

    if 'месяц' in change_text.text:
        pattern = r'через\s*(\d*)\s*(месяц|месяца|месяцев|мес)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + relativedelta(months=1))
            else:
                result_date = (result_date + relativedelta(months=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + relativedelta(months=1))

    if 'год' in change_text.text:
        pattern = r'\s*(\d*)\s*(год|года|лет)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + relativedelta(years=1))
            else:
                result_date = (result_date + relativedelta(years=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + relativedelta(years=1))

    if 'час' in change_text.text:
        pattern = r'через\s*(\d*)\s*(час|часа|часов)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + timedelta(hours=1))
            else:
                result_date = (result_date + timedelta(hours=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + timedelta(hours=1))

    if 'минут' in change_text.text:
        pattern = r'через\s*(\d*)\s*(минут|минуты|минуту|мин)\b'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + timedelta(minutes=1))
            else:
                result_date = (result_date + timedelta(minutes=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + timedelta(minutes=1))

    if 'секунд' in change_text.text:
        pattern = r'через\s*(\d*)\s*(секунд|секунды|секунду|сек)'
        numbers = search(pattern, change_text.text)
        try:
            if numbers.group(1) == '':
                result_date = (result_date + timedelta(seconds=1))
            else:
                result_date = (result_date + timedelta(seconds=int(numbers.group(1))))
            change_text.update_text(change_text.text, pattern)
        except AttributeError:
            result_date = (result_date + timedelta(seconds=1))
    return result_date


async def _parse_time():
    pattern = r'(?:\bв?\s+|\bво\s+)(\d{2})[:.,]?(\d{2})'
    times = search(pattern, change_text.text)
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
            change_text.update_text(change_text.text, pattern)
            return time(hour, minute, second=0)
    return None


async def _parse_dd_mm_yyy():
    pattern = r'\b(\d{2})\.(\d{2})\.(\d{4})\s+(\d{1,2}):(\d{1,2}):(\d{1,2})\b'
    parsed = search(pattern, change_text.text)
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
        change_text.update_text(change_text.text, pattern)
        return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    else:
        return False


async def parse_time_zone(text: str):
    try:
        timezone = search(r'^[+-]\d{1,2}[:.]\d{2}$', text.strip())
        if not timezone:
            return False
        else:
            sign = text[0]
            hours = int(split(r'[:.]', text[1:])[0])
            minutes = int(split(r'[:.]', text[1:])[1])

            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return False

            total_minutes = hours * 60 + minutes

            return total_minutes if sign == '+' else -total_minutes
    except Exception:
        return False


async def corn_trigger(time_zone, text: str):
    _year = ''
    _month = ''
    _week = ''
    _day = ''
    _day_of_week = ''
    _hour = ''
    _minute = ''
    _second = ''
    _timezone = time_zone



    '''
    Каждый/Определенный
    год/месяц/неделю/день/час/минуту/секунду
    
    каждый год 7 марта в 15:00
    
    25 числа каждого месяца
    
    каждый понедельник в 8:00
    
    в рабочие дни с 8-17 каждый час
    
    каждую 3ью неделю в 10 часов 40 минут
    '''
    pass


async def interval_trigger(time_zone, text):
    _weekday = 0
    _day = 0
    _hour = 0
    _minute = 0
    _second = 0
    _start_date = datetime.now()
    _time_zone = FixedOffset(time_zone)
    change_text.text = text

    try:
        if 'недел' in change_text.text:
            pattern = r'\s*(\d*)\s*(неделю|недели|недель|нед)'
            numbers = search(pattern, change_text.text)
            try:
                if numbers.group(1) == '':
                    _weekday = 1
                else:
                    _weekday = int(numbers.group(1))
                change_text.update_text(change_text.text, pattern)
            except AttributeError:
                _weekday = 1

        if 'день' in change_text.text or 'дня' in change_text.text or 'дней' in change_text.text:
            pattern = r'\s*(\d*)\s*(день|дня|дней)'
            numbers = search(pattern, change_text.text)
            try:
                if numbers.group(1) == '':
                    _day = 1
                else:
                    _day = int(numbers.group(1))
                change_text.update_text(change_text.text, pattern)
            except AttributeError:
                _day = 1

        if 'час' in change_text.text:
            pattern = r'\s*(\d*)\s*(час|часа|часов)'
            numbers = search(pattern, change_text.text)
            try:
                if numbers.group(1) == '':
                    _hour = 1
                else:
                    if 0 <= int(numbers.group(1)) <= 23:
                        _hour = int(numbers.group(1))
                    else:
                        _hour = 0
                change_text.update_text(change_text.text, pattern)
            except AttributeError:
                _hour = 1

        if 'мин' in change_text.text:
            pattern = r'\s*(\d*)\s*(минут|минуты|минуту|мин)\b'
            numbers = search(pattern, change_text.text)
            try:
                if numbers.group(1) == '':
                    _minute = 1
                else:
                    if 0 <= int(numbers.group(1)) <= 59:
                        _minute = int(numbers.group(1))
                    else:
                        _minute = 0
                change_text.update_text(change_text.text, pattern)
            except AttributeError:
                _minute = 1

        if 'секунд' in change_text.text:
            pattern = r'\s*(\d*)\s*(секунд|секунды|секунду|сек)'
            numbers = search(pattern, change_text.text)
            try:
                if numbers.group(1) == '':
                    _second = 1
                else:
                    if 0 <= int(numbers.group(1)) <= 59:
                        _second = int(numbers.group(1))
                    else:
                        _second = 1
                change_text.update_text(change_text.text, pattern)
            except AttributeError:
                _second = 1

        return [
            _weekday,
            _day,
            _hour,
            _minute,
            _second,
            _start_date,
            _time_zone
        ]

    except Exception as e:
        logger.error(f'Во время обработки интервальной даты произошла ошибка: {e}')
        raise e

