import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Union


def backtest_binary_predictions(historical_data: Union[np.ndarray, pd.DataFrame],
                                predictions: np.ndarray,
                                is_futures: bool = False,
                                futures_multiplier: int = 10,
                                initial_balance: float = 10000,
                                transaction_fee: float = 1,
                                overnight_holds: bool = False,
                                decision_threshold: float = 0.5,):

    """
    Turns predicted values into binary values to create long or short signal to backtest. Only support 1 or -1 position.

    Args:
        historical_data: One-dimensional numpy array, or a pandas dataframe. Historical data that are attempted to be predicted. Should be the changes of price between opening and closing of positions.
        predictions: One-dimensional numpy array. Predicted values.
        is_futures: Boolean. Use the futures calculation if True.
        futures_multiplier: Integer. The multiplier of futures price to actual balance.
        initial_balance: Float.
        transaction_fee: Float.
        overnight_holds: Boolean. Used in calculation of transaction fee. False implies involve opening and closing of trade is involved on every step.
        decision_threshold: Float between 0 and 1. The threshold for categorizing into 0 or 1.

    Returns:
        One-dimensional numpy array of balance of each date.

    """

    # Check arguments
    if initial_balance <= 0:
        raise ValueError('Initial balance cannot be non-positive.')

    if transaction_fee < 0:
        raise ValueError('Transaction fee cannot be negative')

    if not 0 <= decision_threshold <= 1:
        raise ValueError('Decision Threshold must be between 0 to 1, both inclusive.')

    if len(historical_data) != len(predictions):
        raise IndexError('Length of historical data unequals length of predictions')


    n = len(historical_data)

    # Convert raw predictions into binary predictions
    signals = np.vectorize(lambda x: 1 if x > decision_threshold else -1)(predictions)

    returns = np.array([signals[i] * historical_data[i] for i in range(n)])

    if is_futures:
        if overnight_holds:
            pass
        else:
            pass
    else:
        if overnight_holds:
            pass
        else:
            balances =
