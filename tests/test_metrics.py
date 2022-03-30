import numpy as np
import pytest

from score_analysis import metrics


@pytest.mark.parametrize(
    "metric, expected",
    [
        [metrics.tp, 1],
        [metrics.tn, 4],
        [metrics.fp, 3],
        [metrics.fn, 2],
        [metrics.p, 3],
        [metrics.n, 7],
        [metrics.top, 4],
        [metrics.ton, 6],
        [metrics.pop, 10],
    ],
)
def test_basic_metrics(metric, expected):
    # fmt: off
    matrix = [
        [1, 2],
        [3, 4]
    ]
    # fmt: on
    np.testing.assert_equal(metric(np.asarray(matrix)), expected)
    # Test vectorized version
    np.testing.assert_equal(metric(np.asarray([matrix, matrix])), [expected, expected])


@pytest.mark.parametrize(
    "matrix, expected, isscalar, func",
    [
        # Accuracy
        [[[1, 4], [3, 2]], 0.3, True, metrics.accuracy],
        [[[1, 3, 0], [0, 2, 1], [1, 1, 1]], 0.4, True, metrics.accuracy],
        [[[0, 0], [0, 0]], np.nan, True, metrics.accuracy],
        [[[[1, 4], [3, 2]]], [0.3], False, metrics.accuracy],
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.accuracy],
        # Error rate
        [[[1, 4], [3, 2]], 0.7, True, metrics.error_rate],
        # TPR
        [[[1, 3], [3, 4]], 0.25, True, metrics.tpr],  # Regular computation
        [[[2, 3], [0, 0]], 0.4, True, metrics.tpr],  # Zeros in other row
        [[[0, 0], [0, 0]], np.nan, True, metrics.tpr],  # Nans
        [[[[1, 3], [0, 0]]], [0.25], False, metrics.tpr],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.tpr],  # Vectorized nans
        # TNR
        [[[3, 4], [1, 3]], 0.75, True, metrics.tnr],  # Regular computation
        [[[0, 0], [2, 3]], 0.6, True, metrics.tnr],  # Zeros in other row
        [[[0, 0], [0, 0]], np.nan, True, metrics.tnr],  # Nans
        [[[[0, 0], [1, 3]]], [0.75], False, metrics.tnr],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.tnr],  # Vectorized nans
        # FNR
        [[[1, 3], [3, 4]], 0.75, True, metrics.fnr],  # Regular computation
        [[[2, 3], [0, 0]], 0.6, True, metrics.fnr],  # Zeros in other row
        [[[0, 0], [0, 0]], np.nan, True, metrics.fnr],  # Nans
        [[[[1, 3], [0, 0]]], [0.75], False, metrics.fnr],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.fnr],  # Vectorized nans
        # FPR
        [[[3, 4], [1, 3]], 0.25, True, metrics.fpr],  # Regular computation
        [[[0, 0], [2, 3]], 0.4, True, metrics.fpr],  # Zeros in other row
        [[[0, 0], [0, 0]], np.nan, True, metrics.fpr],  # Nans
        [[[[0, 0], [1, 3]]], [0.25], False, metrics.fpr],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.fpr],  # Vectorized nans
        # PPV
        [[[3, 4], [1, 3]], 0.75, True, metrics.ppv],  # Regular computation
        [[[3, 0], [1, 0]], 0.75, True, metrics.ppv],  # Zeros in other column
        [[[0, 0], [0, 0]], np.nan, True, metrics.ppv],  # Nans
        [[[[3, 0], [1, 0]]], [0.75], False, metrics.ppv],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.ppv],  # Vectorized nans
        # NPV
        [[[3, 4], [1, 1]], 0.2, True, metrics.npv],  # Regular computation
        [[[0, 4], [0, 1]], 0.2, True, metrics.npv],  # Zeros in other column
        [[[0, 0], [0, 0]], np.nan, True, metrics.npv],  # Nans
        [[[[0, 4], [0, 1]]], [0.2], False, metrics.npv],  # Vectorized
        [[[[[0, 0], [0, 0]]]], [[np.nan]], False, metrics.npv],  # Vectorized nans
        # FDR
        [[[3, 4], [1, 3]], 0.25, True, metrics.fdr],  # Regular computation
        # FOR
        [[[3, 4], [1, 1]], 0.8, True, metrics.for_],  # Regular computation
    ],
)
def test_metric(matrix, expected, isscalar, func):
    matrix = np.asarray(matrix)
    expected = np.asarray(expected)
    result = func(matrix)
    np.testing.assert_equal(result, expected)
    assert np.isscalar(result) == isscalar
