from datetime import datetime, date as date_type
from typing import Dict, Optional, Union
from midjourney.domain.i_daily_factors import DailyFactors


class DefaultDailyFactors(DailyFactors):
    def get_factors(self, date: Optional[Union[datetime, date_type]] = None) -> Dict:
        date = self._normalize_to_datetime(date or datetime.now())

        return {
            "date": date.strftime('%Y-%m-%d'),
            "dayOfWeek": date.strftime('%A'),
            "lunarPhase": self._get_lunar_phase(date),
            "timeOfDay": self._get_time_of_day(date.hour),
            "season": self._get_season(date.month),
            "numerology": self._calculate_numerology(date),
            "element": self._get_daily_element(date),
            "planetaryInfluence": self._get_planetary_influence(date.weekday()),
            "luckyColors": self._get_lucky_colors(date),
            "luckyNumbers": self._get_lucky_numbers(date)
        }

    def _normalize_to_datetime(self, dt: Union[datetime, date_type]) -> datetime:
        if isinstance(dt, datetime):
            return dt
        return datetime.combine(dt, datetime.min.time())

    def _get_lunar_phase(self, date: datetime) -> str:
        known_new_moon = datetime(2024, 1, 11)
        days_since = (date - known_new_moon).days
        phase = (days_since % 29.53) / 29.53
        if phase < 0.125:
            return 'New Moon'
        elif phase < 0.25:
            return 'Waxing Crescent'
        elif phase < 0.375:
            return 'First Quarter'
        elif phase < 0.5:
            return 'Waxing Gibbous'
        elif phase < 0.625:
            return 'Full Moon'
        elif phase < 0.75:
            return 'Waning Gibbous'
        elif phase < 0.875:
            return 'Last Quarter'
        else:
            return 'Waning Crescent'

    def _get_time_of_day(self, hour: int) -> str:
        if 5 <= hour < 7:
            return 'Dawn'
        elif 7 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 14:
            return 'Noon'
        elif 14 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 20:
            return 'Dusk'
        else:
            return 'Night'

    def _get_season(self, month: int) -> str:
        if 3 <= month <= 5:
            return 'Spring'
        elif 6 <= month <= 8:
            return 'Summer'
        elif 9 <= month <= 11:
            return 'Autumn'
        else:
            return 'Winter'

    def _calculate_numerology(self, date: datetime) -> int:
        total = sum(map(int, date.strftime("%Y%m%d")))
        while total > 9:
            total = sum(map(int, str(total)))
        return total

    def _get_daily_element(self, date: datetime) -> str:
        elements = ['Fire', 'Water', 'Earth', 'Air', 'Spirit']
        return elements[(date.day + date.month) % len(elements)]

    def _get_planetary_influence(self, weekday: int) -> str:
        return ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'][weekday % 7]

    def _get_lucky_colors(self, date: datetime) -> list:
        colors = ['Gold', 'Silver', 'Rose Gold', 'Emerald', 'Sapphire',
                  'Ruby', 'Amethyst', 'Turquoise', 'Pearl', 'Diamond']
        n = self._calculate_numerology(date)
        return [colors[n - 1], colors[(n + 2) % 10], colors[(n + 5) % 10]]

    def _get_lucky_numbers(self, date: datetime) -> list:
        n = self._calculate_numerology(date)
        return [n, (n + 3) % 10 or 10, (n + 7) % 10 or 10]
