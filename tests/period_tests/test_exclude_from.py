# -*- coding: utf-8 -*-

from pendulum import Period

from .. import (AbstractTestCase, eleventh, fifth, first, fourteenth, fourth,
                ninth, second, seventh, sixth, tenth, third, thirteenth,
                twelfth)


class ExcludeTestcase(AbstractTestCase):

    def assertExcluded(self, from_periods, exclusion, expected=None):
        """Assert that Period.exclude_from was successful.

        Args:
            from_periods (list): List of periods that needs to be excluded from.
            exclusion (Period): Period that needs to be excluded.
            expected (:obj:`list`, optional): Expected result, if None then will use from_periods.
        """
        if expected is None:
            expected = from_periods

        excluded = exclusion.exclude_from(
            *from_periods
        )
        self.assertEqual(
            expected,
            excluded
        )

    def test_exclude_from(self):
        first_period = Period(
            start=third,
            end=sixth
        )
        second_period = Period(
            start=ninth,
            end=twelfth
        )

        starts = [
            first,
            first_period.start
        ]

        assert_tests = []

        for start in starts:

            if start == first:
                # Before/start first period - before first period
                assert_tests.append({
                    'start': start,
                    'end': second
                })

                # Before/start first period - start first period
                assert_tests.append({
                    'start': start,
                    'end': first_period.start
                })

            # Before/start first period - in first period
            assert_tests.append({
                'start': start,
                'end': fourth,
                'expected': [
                    # 4 - 6
                    Period(
                        start=fourth,
                        end=sixth
                    ),
                    # 9 - 12
                    second_period
                ]
            })

            # Before/start first period - end first period
            assert_tests.append({
                'start': start,
                'end': first_period.end,
                'expected': [
                    second_period
                ]
            })

            # Before/start first period - after first period
            assert_tests.append({
                'start': start,
                'end': seventh,
                'expected': [
                    second_period
                ]
            })

            # Before/start first period - start second period
            assert_tests.append({
                'start': start,
                'end': second_period.start,
                'expected': [
                    second_period
                ]
            })

            # Before/start first period - in second period
            assert_tests.append({
                'start': start,
                'end': tenth,
                'expected': [
                    Period(
                        start=tenth,
                        end=second_period.end
                    )
                ]
            })

            # Before/start first period - end second period
            assert_tests.append({
                'start': start,
                'end': second_period.end,
                'expected': []
            })

            # Before/start first period - after second period
            assert_tests.append({
                'start': start,
                'end': thirteenth,
                'expected': []
            })

        # In first period - in first period
        assert_tests.append({
            'start': fourth,
            'end': fifth,
            'expected': [
                # 3 - 4
                Period(
                    start=first_period.start,
                    end=fourth
                ),
                # 5 - 6
                Period(
                    start=fifth,
                    end=first_period.end
                ),
                # 9 - 12
                second_period
            ]
        })

        # In first period - end first period
        assert_tests.append({
            'start': fourth,
            'end': first_period.end,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                ),
                second_period
            ]
        })

        # In first period - after first period
        assert_tests.append({
            'start': fourth,
            'end': seventh,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                ),
                second_period
            ]
        })

        # In first period - start second period
        assert_tests.append({
            'start': fourth,
            'end': second_period.start,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                ),
                second_period
            ]
        })

        # In first period - in second period
        assert_tests.append({
            'start': fourth,
            'end': tenth,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                ),
                Period(
                    start=tenth,
                    end=second_period.end
                )
            ]
        })

        # In first period - end second period
        assert_tests.append({
            'start': fourth,
            'end': second_period.end,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                )
            ]
        })

        # In first period - after second period
        assert_tests.append({
            'start': fourth,
            'end': thirteenth,
            'expected': [
                Period(
                    start=first_period.start,
                    end=fourth
                )
            ]
        })

        # End first period - after first period
        assert_tests.append({
            'start': first_period.end,
            'end': seventh,
        })

        # End first period - start second period
        assert_tests.append({
            'start': first_period.end,
            'end': second_period.start,
        })

        # After first period - start second period
        assert_tests.append({
            'start': seventh,
            'end': second_period.start,
        })

        mids = [
            first_period.end, seventh,
            second_period.start
        ]

        for mid in mids:
            # End/after first periods or start second period - in second period
            assert_tests.append({
                'start': mid,
                'end': tenth,
                'expected': [
                    first_period,
                    Period(
                        start=tenth,
                        end=second_period.end
                    )
                ]
            })

            # End/after first periods or start second period - end second period
            assert_tests.append({
                'start': mid,
                'end': second_period.end,
                'expected': [
                    first_period
                ]
            })

            # End/after first periods or start second period - after second period
            assert_tests.append({
                'start': mid,
                'end': thirteenth,
                'expected': [
                    first_period
                ]
            })

        # In second period - in second period
        assert_tests.append({
            'start': tenth,
            'end': eleventh,
            'expected': [
                first_period,
                Period(
                    start=second_period.start,
                    end=tenth
                ),
                Period(
                    start=eleventh,
                    end=second_period.end
                )
            ]
        })

        # In second period - end second period
        assert_tests.append({
            'start': tenth,
            'end': second_period.end,
            'expected': [
                first_period,
                Period(
                    start=second_period.start,
                    end=tenth
                )
            ]
        })

        # In second period - after second period
        assert_tests.append({
            'start': tenth,
            'end': thirteenth,
            'expected': [
                first_period,
                Period(
                    start=second_period.start,
                    end=tenth
                )
            ]
        })

        ends = [
            second_period.end,
            thirteenth
        ]

        for end in ends:
            # End second period - after second period
            assert_tests.append({
                'start': end,
                'end': fourteenth,
            })

        for assert_test in assert_tests:
            self.assertExcluded(
                from_periods=[
                    first_period,
                    second_period
                ],
                exclusion=Period(
                    start=assert_test['start'],
                    end=assert_test['end']
                ),
                expected=assert_test.get('expected')
            )
