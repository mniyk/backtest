"""backtest.pyのunittest
"""
import time
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

        self.order_count = 1
        self.profit = 500
        self.loss = 50
        self.pip = 0.01

        self.ranges = {
            'macd_signal_9': {'ask': [0, 10], 'bid': [0, -10]}}
        self.reverse_order = True

        self.back = Backtest(
            self.df, 
            'close', 
            'high', 
            'low', 
            self.order_count, 
            self.profit, 
            self.loss, 
            self.pip)

    @staticmethod
    def direction_ranges(data, columns, **kwargs):
        directions = []

        for k, v in kwargs['ranges'].items():
            direction = 0
            index = columns.get_loc(k)
            val = data[index]

            if v['ask'][0] < val <= v['ask'][1]:
                direction = 1
                    
            if v['bid'][0] > val >= v['bid'][1]:
                direction = -1

            directions.append(direction)

        result = 0

        if abs(sum(directions)) == len(directions):
            if sum(directions) > 0:
                result = 1
            elif sum(directions) < 0:
                result = -1

        return result

    def test_backtest_direction_range(self) -> None:
        start_time = time.time()

        self.back.backtest(
            self.direction_ranges,
            reverse_order=self.reverse_order,
            ranges=self.ranges)

        print(self.back.result_df)

        print(f'processing time: {time.time() - start_time}')

    def test_performance(self):
        self.back.backtest(
            self.direction_ranges,
            reverse_order=self.reverse_order,
            ranges=self.ranges)

        performance = self.back.performance(
            self.back.result_df, 
            self.profit, 
            self.loss)
        
        print(performance)

    def test_check_backtest_data(self):
        self.back.backtest(
            self.direction_ranges,
            reverse_order=self.reverse_order,
            ranges=self.ranges)

        merge_df = pd.merge(
            self.df,
            self.back.result_df,
            how='outer',
            left_on='time',
            right_on='order_time')

        merge_df.to_csv('data.csv')
