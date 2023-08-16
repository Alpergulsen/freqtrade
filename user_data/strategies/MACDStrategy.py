
# --- Do not remove these libs ---
from freqtrade.strategy import IStrategy
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
from pandas import DataFrame
# --------------------------------

import talib.abstract as ta


class MACDStrategy(IStrategy):
    """
    author@: Gert Wohlgemuth

    idea:

        uptrend definition:
            MACD above MACD signal
            and CCI < -50

        downtrend definition:
            MACD below MACD signal
            and CCI > 100

    freqtrade hyperopt --strategy MACDStrategy --hyperopt-loss <someLossFunction> --spaces buy sell

    The idea is to optimize only the CCI value.
    - Buy side: CCI between -700 and 0
    - Sell side: CCI between 0 and 700

    """
    INTERFACE_VERSION: int = 3
    exit_profit_only = True
    sell_profit_offset: 0.01
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.60

    # Optimal timeframe for the strategy
    timeframe = '5m'

    buy_cci = IntParameter(low=-700, high=0, default=-50, space='buy', optimize=True)
    sell_cci = IntParameter(low=0, high=700, default=100, space='sell', optimize=True)

    # Buy hyperspace params:
    buy_params = {
        "buy_cci": -48,
    }

    # Sell hyperspace params:
    sell_params = {
        "sell_cci": 687,

    }

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        dataframe['cci'] = ta.CCI(dataframe)
        dataframe['rsi'] = ta.RSI(dataframe)
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['rsi5'] = ta.RSI(dataframe, timeperiod=5)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['rsi5'] > dataframe['ema5'])&
                (dataframe['rsi5'] < 50) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'enter_long'] = 1
        dataframe.loc[
            (
                (dataframe['rsi5'] > 50) 
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > 78)
            ),
            'exit_long'] = 1
        dataframe.loc[
            (
                (dataframe['rsi'] < 30)
            ),
            'exit_short'] = 1

        return dataframe