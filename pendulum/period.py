# -*- coding: utf-8 -*-

import operator
from datetime import date, datetime

import pendulum

from .constants import MONTHS_PER_YEAR
from .helpers import precise_diff
from .interval import BaseInterval, Interval
from .mixins.interval import WordableIntervalMixin


class Period(WordableIntervalMixin, BaseInterval):
    """
    Interval class that is aware of the datetimes that generated the
    time difference.
    """

    def __new__(cls, start, end, absolute=False):
        if absolute and start > end:
            end, start = start, end

        if isinstance(start, pendulum.Pendulum):
            start = start._datetime
        elif isinstance(start, pendulum.Date):
            start = date(start.year, start.month, start.day)

        if isinstance(end, pendulum.Pendulum):
            end = end._datetime
        elif isinstance(end, pendulum.Date):
            end = date(end.year, end.month, end.day)

        delta = end - start

        return super(Period, cls).__new__(
            cls, seconds=delta.total_seconds()
        )

    def __init__(self, start, end, absolute=False):
        super(Period, self).__init__()

        if not isinstance(start, (pendulum.Date)):
            if isinstance(start, datetime):
                start = pendulum.Pendulum.instance(start)
            else:
                start = pendulum.Date.instance(start)

            _start = start
        else:
            if isinstance(start, pendulum.Pendulum):
                _start = start._datetime
            else:
                _start = date(start.year, start.month, start.day)

        if not isinstance(end, (pendulum.Date)):
            if isinstance(end, datetime):
                end = pendulum.Pendulum.instance(end)
            else:
                end = pendulum.Date.instance(end)

            _end = end
        else:
            if isinstance(end, pendulum.Pendulum):
                _end = end._datetime
            else:
                _end = date(end.year, end.month, end.day)

        self._invert = False
        if start > end:
            self._invert = True

            if absolute:
                end, start = start, end
                _end, _start = _start, _end

        self._absolute = absolute
        self._start = start
        self._end = end
        self._delta = precise_diff(_start, _end)

    @property
    def years(self):
        return self._delta['years']

    @property
    def months(self):
        return self._delta['months']

    @property
    def weeks(self):
        return self._delta['days'] // 7

    @property
    def days(self):
        return self._days

    @property
    def remaining_days(self):
        return abs(self._delta['days']) % 7 * self._sign(self._days)

    @property
    def hours(self):
        return self._delta['hours']

    @property
    def minutes(self):
        return self._delta['minutes']

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def in_years(self):
        """
        Gives the duration of the Period in full years.

        :rtype: int
        """
        return self.years

    def in_months(self):
        """
        Gives the duration of the Period in full months.

        :rtype: int
        """
        return self.years * MONTHS_PER_YEAR + self.months

    def in_weekdays(self):
        start, end = self.start.start_of('day'), self.end.start_of('day')
        if not self._absolute and self.invert:
            start, end = self.end.start_of('day'), self.start.start_of('day')

        days = 0
        while start <= end:
            if start.is_weekday():
                days += 1

            start = start.add(days=1)

        return days * (-1 if not self._absolute and self.invert else 1)

    def in_weekend_days(self):
        start, end = self.start.start_of('day'), self.end.start_of('day')
        if not self._absolute and self.invert:
            start, end = self.end.start_of('day'), self.start.start_of('day')

        days = 0
        while start <= end:
            if start.is_weekend():
                days += 1

            start = start.add(days=1)

        return days * (-1 if not self._absolute and self.invert else 1)

    def in_words(self, locale=None, separator=' '):
        """
        Get the current interval in words in the current locale.

        Ex: 6 jours 23 heures 58 minutes

        :param locale: The locale to use. Defaults to current locale.
        :type locale: str

        :param separator: The separator to use between each unit
        :type separator: str

        :rtype: str
        """
        periods = [
            ('year', self.years),
            ('month', self.months),
            ('week', self.weeks),
            ('day', self.remaining_days),
            ('hour', self.hours),
            ('minute', self.minutes),
            ('second', self.remaining_seconds)
        ]

        return super(Period, self).in_words(
            locale=locale, separator=separator, _periods=periods
        )

    def range(self, unit, amount=1):
        return list(self.xrange(unit, amount))

    def xrange(self, unit, amount=1):
        method = 'add'
        op = operator.le
        if not self._absolute and self.invert:
            method = 'subtract'
            op = operator.ge

        start, end = self.start, self.end

        i = amount
        while op(start, end):
            yield start

            start = getattr(self.start, method)(**{unit: i})

            i += amount

    def intersect(self, *periods):
        """
        Return the Period intersection of the current Period
        and the given periods.

        :type periods: tuple of Period

        :rtype: Period
        """
        start, end = self.start, self.end
        has_intersection = False
        for period in periods:
            if period.end < start or period.start > end:
                continue

            has_intersection = True
            start = max(start, period.start)
            end = min(end, period.end)

        if not has_intersection:
            return None

        return self.__class__(start, end)

    def as_interval(self):
        """
        Return the Period as an Interval.

        :rtype: Interval
        """
        return Interval(seconds=self.total_seconds())

    def exclude(self, *periods):
        """Exclude a list of periods from this period.

        Args:
            *periods (tuple): Tuple of periods that need to be excluded from this period.

        Returns:
            list: List of periods resulting from the exclusion.
        """
        if not periods:
            return [self]

        period = periods[0]
        remaining_periods = periods[1:]

        excluded_periods = self._exclude(other=period)
        if not remaining_periods:
            return excluded_periods

        result = []
        for excluded_period in excluded_periods:
            result.extend(
                excluded_period.exclude(
                    *remaining_periods
                ) or []
            )
        return result

    def exclude_from(self, *periods):
        """Exclude this period from a list of periods.

        Args:
            *periods (tuple): Tuple of periods that this period needs to be excluded from.

        Returns:
            list: List of periods resulting from the exclusion.
        """

        all_excluded_periods = []
        periods = list(periods)

        for period in periods:
            excluded_periods = period._exclude(other=self)
            if excluded_periods is not None:
                all_excluded_periods += excluded_periods

        return all_excluded_periods

    def _exclude(self, other):
        """Exclude this period from another period.

        Args:
            self (Period): Period from which need to be excluded.

        Returns:
            list: List of periods resulting from the exclusion.
        """
        excluded_periods = []
        this = self
        if other.end > self.start:
            if other.start <= self.start:
                if other.end < self.end:
                    this = Period(
                        start=other.end,
                        end=self.end
                    )
                else:
                    # Do not add it (remove it)
                    return None
            elif other.start < self.end:
                if other.end < self.end:
                    # Insert a period before new one, the other splits
                    # a period in two periods.
                    excluded_periods.append(
                        Period(
                            start=self.start,
                            end=other.start
                        )
                    )
                    this = Period(
                        start=other.end,
                        end=self.end
                    )
                else:
                    this = Period(
                        start=self.start,
                        end=other.start
                    )
        excluded_periods.append(this)
        return excluded_periods

    def merge(self, *periods):
        return self.merge_periods(
            self, *periods
        )

    @classmethod
    def merge_periods(cls, *periods):
        if len(periods) == 0:
            return []

        periods = list(periods)

        periods.sort()

        period = periods[0]
        merged_periods = []

        for i in range(1, len(periods)):
            next_period = periods[i]

            if next_period.start <= period.end:
                if next_period.end > period.end:
                    period = Period(
                        start=period.start,
                        end=next_period.end
                    )
                continue
            else:
                merged_periods.append(
                    period
                )
                period = next_period

        merged_periods.append(
            period
        )
        return merged_periods

    def __iter__(self):
        return self.xrange('days')

    def __contains__(self, item):
        from .pendulum import Pendulum

        if not isinstance(item, Pendulum):
            item = Pendulum.instance(item)

        return item.between(self.start, self.end)

    def __add__(self, other):
        return self.as_interval().__add__(other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.as_interval().__sub__(other)

    def __neg__(self):
        return self.__class__(self.end, self.start, self._absolute)

    def __mul__(self, other):
        return self.as_interval().__mul__(other)

    __rmul__ = __mul__

    def __floordiv__(self, other):
        return self.as_interval().__floordiv__(other)

    def __truediv__(self, other):
        return self.as_interval().__truediv__(other)

    __div__ = __floordiv__

    def __mod__(self, other):
        return self.as_interval().__mod__(other)

    def __divmod__(self, other):
        return self.as_interval().__divmod__(other)

    def __abs__(self):
        return self.__class__(self.start, self.end, True)

    def __repr__(self):
        return '<Period [{} -> {}]>'.format(
            self._start, self._end
        )

    def __lt__(self, other):
        if self.start == other.start:
            return self.end < other.end
        return self.start < other.start

    def _getstate(self, protocol=3):
        start, end = self.start, self.end

        if self._invert and self._absolute:
            end, start = start, end

        return (
            start, end, self._absolute
        )

    def __reduce__(self):
        return self.__reduce_ex__(2)

    def __reduce_ex__(self, protocol):
        return self.__class__, self._getstate(protocol)
