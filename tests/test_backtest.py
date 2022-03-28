"""backtest.pyのunittest
"""
import logging
import unittest

import pandas as pd

from backtest.backtest import Backtest


logging.basicConfig(
    level=logging.DEBUG,
    format='\t'.join([
        '%(asctime)s',
        '%(levelname)s',
        '%(filename)s',
        '%(funcName)s',
        '%(processName)s',
        '%(process)d',
        '%(threadName)s',
        '%(thread)d',
        '%(message)s']))

logger = logging.getLogger(__name__)


class TestOanda(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.read_pickle('tests/data.pickle')

        self.back = Backtest(
            self.df.iloc[-100:, :], 'close', 'high', 'low', 1, 10, 10, 0.01)

    @staticmethod
    def backtest_direction(data):
        direction = None

        if data['macd_12_26_shift_diff'] > 0:
            direction = 1

        if data['macd_12_26_shift_diff'] < 0:
            direction = -1

        return direction

    def test_backtest(self) -> None:
        self.back.backtest(self.backtest_direction, kwargs=None)

        print(self.back.result_df)

    def test_performance(self):
        self.back.backtest(self.backtest_direction, kwargs=None)

        performance = self.back.performance(self.back.result_df, 10, 10)
        
        print(performance)
