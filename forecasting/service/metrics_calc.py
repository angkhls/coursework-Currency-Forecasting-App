import numpy as np


def mape(actual: list[float], predicted: list[float]) -> float:
    actual_arr = np.array(actual, dtype=float)
    pred_arr = np.array(predicted, dtype=float)
    mask = actual_arr != 0
    if not mask.any():
        return 0.0
    return float(np.mean(np.abs((actual_arr[mask] - pred_arr[mask]) / actual_arr[mask])) * 100)


def rmse(actual: list[float], predicted: list[float]) -> float:
    actual_arr = np.array(actual, dtype=float)
    pred_arr = np.array(predicted, dtype=float)
    return float(np.sqrt(np.mean((actual_arr - pred_arr) ** 2)))
