import logging

import pandas as pd
from pandas import DataFrame, Series


logger = logging.getLogger(__name__)


class Backtest:
    """バックテストのクラス
    """
    def __init__(
        self, 
        df: DataFrame,
        close_column: str, 
        high_column: str, 
        low_column: str, 
        order_count: int, 
        profit: int, 
        loss: int,
        pip: float) -> None:
        """初期化

        Args:
            df (DataFrame): ローソク足データ
            close_column (str): 終値の列名
            high_column (str): 高値の列名
            low_column (str): 安値の列名
            order_count (int): 注文数
            profit (int): 利益
            loss (int): 損失
            pip (float): pip

        Examples:
            >>> back = Backtest(
                    df, 'close', 'high', 'low', 1, 10, 10, 0.01)
        """
        self.df = df
        self.close_column = close_column
        self.high_column = high_column
        self.low_column = low_column
        self.order_count = order_count
        self.profit = profit
        self.loss = loss
        self.pip = pip
        self.orders = {'ask': [], 'bid': []}
        self.settlements = []
        self.result_df = None

        self.time_index = 0
        self.close_index = df.columns.get_loc(self.close_column)
        self.high_index = df.columns.get_loc(self.high_column)
        self.low_index = df.columns.get_loc(self.low_column)

    def backtest(self, func, reverse_order=False, **kwargs):
        """バックテスト
        """
        columns = self.df.columns

        for data in self.df.values:
            self.order_settlement(data)

            if kwargs:
                direction = func(data, columns, **kwargs)
            else:
                direction = func(data, columns)

            self.send_order(data, direction)

            if reverse_order:
                self.send_order(data, direction * -1)

        if self.result_df is None:
            self.result_df = pd.DataFrame.from_dict(self.settlements)
        else:
            self.result_df = self.join_dfs(
                [self.result_df, pd.DataFrame.from_dict(self.settlements)])

    def send_order(self, data, direction: int):
        """発注

        Args:
            data (Series): ローソク足データ
            direction (int): 売買方向
        """
        close_price = data[self.close_index]
        profit_pip = self.profit * self.pip
        loss_pip = self.loss * self.pip

        result = {
            'order_time': data[self.time_index],
            'order_price': close_price,
            'direction': direction,
            'profit_price': None,
            'loss_price': None,
            'settlement_time': None,
            'settlement_price': None,
            'result': None}

        if direction == 1:
            if len(self.orders['ask']) < self.order_count:
                result['profit_price'] = close_price + profit_pip
                result['loss_price'] = close_price - loss_pip

                self.orders['ask'].append(result)
        elif direction == -1:
            if len(self.orders['bid']) < self.order_count:
                result['profit_price'] = close_price - profit_pip
                result['loss_price'] = close_price + loss_pip

                self.orders['bid'].append(result)

    def order_settlement(self, data: Series):
        """決済

        Args:
            data (Series): ローソク足データ
        """
        high_price = data[self.high_index]
        low_price = data[self.low_index]

        for key in self.orders:
            pops = []

            for i in range(len(self.orders[key])):
                result = 0
                profit_price = self.orders[key][i]['profit_price']
                loss_price = self.orders[key][i]['loss_price']
                
                if key == 'ask':
                    if loss_price >= low_price:
                        settlement_price = low_price
                        result = -1
                    else:
                        if profit_price < high_price:
                            settlement_price = high_price
                            result = 1
                elif key == 'bid':
                    if loss_price <= high_price:
                        settlement_price = high_price
                        result = -1
                    else:
                        if profit_price > low_price:
                            settlement_price = low_price
                            result = 1
                
                if result != 0:
                    self.orders[
                        key][i]['settlement_time'] = data[self.time_index]
                    self.orders[key][i]['settlement_price'] = settlement_price
                    self.orders[key][i]['result'] = result

                    self.settlements.append(self.orders[key][i])

                    pops.append(i)

            pops.reverse()

            for i in pops:
                self.orders[key].pop(i)
    
    @classmethod
    def performance(cls, backtest_df, profit, loss):
        """実績
        """
        profit_count = backtest_df[
            backtest_df['result'] == 1]['result'].count()
        loss_count = backtest_df[
            backtest_df['result'] == -1]['result'].count()
        total_count = profit_count + loss_count
        profit_rate = round((profit_count / total_count) * 100, 0)

        profit_and_loss = (
            (profit_count * profit) - (loss_count * loss))

        return {
            'total_count': total_count,
            'ptofit_count': profit_count,
            'loss_count': loss_count,
            'profit_rate': profit_rate,
            'profit_and_loss': profit_and_loss,
            'profit': profit,
            'loss': loss}
