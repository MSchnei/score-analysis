import numpy as np
import pytest

from score_analysis.scores import Scores, pointwise_cm


def test_from_labels():
    scores = Scores.from_labels(labels=[2, 2, 3], scores=[3, 2, 1], pos_label=2)
    np.testing.assert_equal(scores.pos, [2, 3])
    np.testing.assert_equal(scores.neg, [1])


def test_properties():
    scores = Scores(
        pos=[1, 2, 3],
        neg=[6],
        nb_easy_pos=2,
        nb_easy_neg=4,
    )
    assert scores.hard_pos_ratio == 0.6
    assert scores.hard_neg_ratio == 0.2
    assert scores.easy_pos_ratio == 0.4
    assert scores.easy_neg_ratio == 0.8
    assert scores.nb_easy_samples == 6
    assert scores.nb_hard_samples == 4
    assert scores.nb_all_samples == 10
    assert scores.easy_ratio == 0.6
    assert scores.hard_ratio == 0.4

    scores = Scores(pos=[], neg=[], nb_easy_pos=0, nb_easy_neg=0)
    assert scores.hard_pos_ratio == 1.0
    assert scores.hard_neg_ratio == 1.0
    assert scores.easy_pos_ratio == 0.0
    assert scores.easy_neg_ratio == 0.0
    assert scores.nb_easy_samples == 0
    assert scores.nb_hard_samples == 0
    assert scores.nb_all_samples == 0
    assert scores.easy_ratio == 0.0
    assert scores.hard_ratio == 1.0


@pytest.mark.parametrize(
    "pos, neg, threshold, score_class, equal_class, expected",
    [
        # Normal case, all scores and threshold are unique
        [[0, 1, 2, 3], [0], 2.5, "pos", "pos", [[1, 3], [0, 1]]],
        # No positive scores
        [[], [0], 1.5, "pos", "pos", [[0, 0], [0, 1]]],
        # No negative scores
        [[0], [], 1.5, "pos", "pos", [[0, 1], [0, 0]]],
        # Count threshold to pos
        [[0, 1, 1, 2, 3], [1, 1, 2], 1, "pos", "pos", [[4, 1], [3, 0]]],
        [[1, 1, 2], [0, 1, 1, 2, 3], 1, "pos", "pos", [[3, 0], [4, 1]]],
        # Count threshold to neg
        [[0, 1, 1, 2, 3], [1, 1, 2], 1, "pos", "neg", [[2, 3], [1, 2]]],
        [[1, 1, 2], [0, 1, 1, 2, 3], 1, "pos", "neg", [[1, 2], [2, 3]]],
        # Reverse score direction
        [[0, 1, 2, 3], [0], 2.5, "neg", "pos", [[3, 1], [1, 0]]],
        # Reverse score direction with threshold equal to scores, count to pos
        [[0, 1, 1, 2, 3], [1, 1, 2], 1, "neg", "pos", [[3, 2], [2, 1]]],
        [[1, 1, 2], [0, 1, 1, 2, 3], 1, "neg", "pos", [[2, 1], [3, 2]]],
        # Reverse score direction with threshold equal to scores, count to neg
        [[0, 1, 1, 2, 3], [1, 1, 2], 1, "neg", "neg", [[1, 4], [0, 3]]],
        [[1, 1, 2], [0, 1, 1, 2, 3], 1, "neg", "neg", [[0, 3], [1, 4]]],
        # Threshold lower than all scores
        [[0, 1, 2], [0, 1, 2], -1, "pos", "pos", [[3, 0], [3, 0]]],
        [[0, 1, 2], [0, 1, 2], -1, "neg", "pos", [[0, 3], [0, 3]]],
        # Threshold higher than all scores
        [[0, 1, 2], [0, 1, 2], 3, "pos", "pos", [[0, 3], [0, 3]]],
        [[0, 1, 2], [0, 1, 2], 3, "neg", "pos", [[3, 0], [3, 0]]],
        # Threshold at lower extreme value
        [[0, 1, 2], [0, 1, 2], 0, "pos", "pos", [[3, 0], [3, 0]]],
        [[0, 1, 2], [0, 1, 2], 0, "pos", "neg", [[2, 1], [2, 1]]],
        [[0, 1, 2], [0, 1, 2], 0, "neg", "pos", [[1, 2], [1, 2]]],
        [[0, 1, 2], [0, 1, 2], 0, "neg", "neg", [[0, 3], [0, 3]]],
        # Threshold at higher extreme value
        [[0, 1, 2], [0, 1, 2], 2, "pos", "pos", [[1, 2], [1, 2]]],
        [[0, 1, 2], [0, 1, 2], 2, "pos", "neg", [[0, 3], [0, 3]]],
        [[0, 1, 2], [0, 1, 2], 2, "neg", "pos", [[3, 0], [3, 0]]],
        [[0, 1, 2], [0, 1, 2], 2, "neg", "neg", [[2, 1], [2, 1]]],
        # Vectorized version
        [[0, 1, 2, 3], [0], [[2.5]], "pos", "pos", [[[[1, 3], [0, 1]]]]],
    ],
)
def test_cm(pos, neg, threshold, score_class, equal_class, expected):
    scores = Scores(pos, neg, score_class=score_class, equal_class=equal_class)
    cm = scores.cm(threshold)
    np.testing.assert_equal(cm.matrix, expected)


@pytest.mark.parametrize(
    "pos, neg, threshold, expected",
    [
        # Simple scalar version
        [[0, 1, 2, 3], [0, 1, 2], 1.5, 0.5],
        # Vectorized version
        [[0, 1, 2, 3], [], [-1, 0, 1.5, 3, 4], [1.0, 1.0, 0.5, 0.25, 0.0]],
    ],
)
def test_tpr(pos, neg, threshold, expected):
    scores = Scores(pos, neg)
    tpr = scores.tpr(threshold)
    np.testing.assert_equal(tpr, expected)


def test_fnr_etc():
    scores = Scores(pos=[0, 1, 2, 3], neg=[0, 1, 2, 3, 4])
    tpr = scores.tpr(threshold=2.5)
    np.testing.assert_allclose(tpr, 0.25)

    fnr = scores.fnr(threshold=2.5)
    np.testing.assert_allclose(fnr, 0.75)

    tnr = scores.tnr(threshold=2.5)
    np.testing.assert_allclose(tnr, 0.6)

    fpr = scores.fpr(threshold=2.5)
    np.testing.assert_allclose(fpr, 0.4)


@pytest.mark.parametrize(
    "pos, tpr, score_class, equal_class, expected",
    [
        # First example
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "pos", [4, 4, 3, 2, 1]],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "pos", [4, 3.5, 2.5, 1.5]],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "neg", [4, 3, 2, 1, 1]],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "neg", [3.5, 2.5, 1.5, 1]],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "pos", [1, 1, 2, 3, 4]],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "pos", [1, 1.5, 2.5, 3.5]],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "neg", [1, 2, 3, 4, 4]],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "neg", [1.5, 2.5, 3.5, 4]],
        # Simple interpolation
        [[0, 1], 0.6, "pos", "pos", 0.8],
        [[0, 1], 0.6, "pos", "neg", 0],
        [[0, 1], 0.6, "neg", "pos", 0.2],
        [[0, 1], 0.6, "neg", "neg", 1],
        # Edge cases
        [[0, 1], -0.1, "pos", "pos", 1],
        [[0, 1], 1.1, "pos", "pos", 0],
    ],
)
def test_threshold_at_tpr(pos, tpr, score_class, equal_class, expected):
    scores = Scores(pos, [], score_class=score_class, equal_class=equal_class)
    threshold = scores.threshold_at_tpr(tpr=tpr)
    np.testing.assert_allclose(threshold, expected, atol=1e-10)


@pytest.mark.parametrize(
    "pos, neg, topr, score_class, equal_class, expected",
    [
        # First example
        [
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [0, 0.25, 0.5, 0.75, 1],
            "pos",
            "pos",
            [4, 4, 3, 2, 1],
        ],
        [
            [1, 3, 5, 7],
            [2, 4, 6, 8],
            [0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375],
            "pos",
            "pos",
            [8, 7.5, 6.5, 5.5, 4.5, 3.5, 2.5, 1.5],
        ],
        [
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [0, 0.25, 0.5, 0.75, 1],
            "pos",
            "neg",
            [4, 3, 2, 1, 1],
        ],
        [
            [1, 3, 5, 7],
            [2, 4, 6, 8],
            [0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375],
            "pos",
            "neg",
            [7.5, 6.5, 5.5, 4.5, 3.5, 2.5, 1.5, 1],
        ],
        [
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [0, 0.25, 0.5, 0.75, 1],
            "neg",
            "pos",
            [1, 1, 2, 3, 4],
        ],
        [
            [1, 3, 5, 7],
            [2, 4, 6, 8],
            [0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375],
            "neg",
            "pos",
            [1, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5],
        ],
        [
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            [0, 0.25, 0.5, 0.75, 1],
            "neg",
            "neg",
            [1, 2, 3, 4, 4],
        ],
        [
            [1, 3, 5, 7],
            [2, 4, 6, 8],
            [0.0625, 0.1875, 0.3125, 0.4375, 0.5625, 0.6875, 0.8125, 0.9375],
            "neg",
            "neg",
            [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8],
        ],
        # Simple interpolation
        [[0, 1], [0, 1], 0.6, "pos", "pos", 0.6],
        [[0, 1], [0, 1], 0.6, "pos", "neg", 0],
        [[0, 1], [0, 1], 0.6, "neg", "pos", 0.4],
        [[0, 1], [0, 1], 0.6, "neg", "neg", 1],
        # Edge cases
        [[0, 1], [0, 1], -0.1, "pos", "pos", 1],
        [[0, 1], [0, 1], 1.1, "pos", "pos", 0],
    ],
)
def test_threshold_at_topr(pos, neg, topr, score_class, equal_class, expected):
    scores = Scores(pos, neg, score_class=score_class, equal_class=equal_class)
    threshold = scores.threshold_at_topr(topr=topr)
    np.testing.assert_allclose(threshold, expected, atol=1e-10)


def test_invalid_threshold_at_tpr_etc():
    with pytest.raises(ValueError):
        Scores(pos=[], neg=[1, 2]).threshold_at_tpr(0.5)
    with pytest.raises(ValueError):
        Scores(pos=[], neg=[1, 2]).threshold_at_fnr(0.5)
    with pytest.raises(ValueError):
        Scores(pos=[1, 2], neg=[]).threshold_at_tnr(0.5)
    with pytest.raises(ValueError):
        Scores(pos=[1, 2], neg=[]).threshold_at_fpr(0.5)
    with pytest.raises(ValueError):
        Scores(pos=[], neg=[]).threshold_at_topr(0.5)
    with pytest.raises(ValueError):
        Scores(pos=[], neg=[]).threshold_at_tonr(0.5)


@pytest.mark.parametrize(
    "scores, ratio, score_class, equal_class",
    [
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "pos"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "pos"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "neg"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "neg"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "pos"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "pos"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "neg"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "neg"],
        # Simple interpolation
        [[0, 1], 0.6, "pos", "pos"],
        [[0, 1], 0.6, "pos", "neg"],
        [[0, 1], 0.6, "neg", "pos"],
        [[0, 1], 0.6, "neg", "neg"],
        # Edge cases
        [[0, 1], -0.1, "pos", "pos"],
        [[0, 1], 1.1, "pos", "pos"],
    ],
)
def test_threshold_setting(scores, ratio, score_class, equal_class):
    # We reduce the other cases (FNR, TNR and FPR) to TPR calculations
    score_obj = Scores(scores, [], score_class=score_class, equal_class=equal_class)
    expected = score_obj.threshold_at_tpr(ratio)

    # FNR
    score_obj = Scores(scores, [], score_class=score_class, equal_class=equal_class)
    threshold = score_obj.threshold_at_fnr(1.0 - np.asarray(ratio))
    np.testing.assert_allclose(threshold, expected, atol=1e-10)

    # TNR
    reverse_class = "neg" if equal_class == "pos" else "pos"
    score_obj = Scores([], scores, score_class=score_class, equal_class=reverse_class)
    threshold = score_obj.threshold_at_tnr(1.0 - np.asarray(ratio))
    np.testing.assert_allclose(threshold, expected, atol=1e-10)

    # FPR
    reverse_class = "neg" if equal_class == "pos" else "pos"
    score_obj = Scores([], scores, score_class=score_class, equal_class=reverse_class)
    threshold = score_obj.threshold_at_fpr(ratio)
    np.testing.assert_allclose(threshold, expected, atol=1e-10)


@pytest.mark.parametrize(
    "scores, ratio, score_class, equal_class",
    [
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "pos"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "pos"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "pos", "neg"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "pos", "neg"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "pos"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "pos"],
        [[1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1], "neg", "neg"],
        [[1, 2, 3, 4], [0.125, 0.375, 0.625, 0.875], "neg", "neg"],
        # Simple interpolation
        [[0, 1], 0.6, "pos", "pos"],
        [[0, 1], 0.6, "pos", "neg"],
        [[0, 1], 0.6, "neg", "pos"],
        [[0, 1], 0.6, "neg", "neg"],
        # Edge cases
        [[0, 1], -0.1, "pos", "pos"],
        [[0, 1], 1.1, "pos", "pos"],
    ],
)
def test_threshold_setting_outcome(scores, ratio, score_class, equal_class):
    # We reduce TONR to TOPR calculations
    score_obj = Scores(scores, [], score_class=score_class, equal_class=equal_class)
    expected = score_obj.threshold_at_topr(ratio)

    # TONR
    reverse_class = "neg" if equal_class == "pos" else "pos"
    score_obj = Scores([], scores, score_class=score_class, equal_class=reverse_class)
    threshold = score_obj.threshold_at_tonr(1.0 - np.asarray(ratio))
    np.testing.assert_allclose(threshold, expected, atol=1e-10)


def test_threshold_setting_easy_pos():
    """Testing threshold setting in the presence of easy positive samples."""
    scores = Scores(pos=range(100), neg=[])
    scores_easy = Scores(pos=range(40), neg=[], nb_easy_pos=60)

    tpr = [0.7, 0.8, 0.9, 0.912]
    np.testing.assert_allclose(
        scores.threshold_at_tpr(tpr), scores_easy.threshold_at_tpr(tpr)
    )

    fnr = [0.02, 0.045, 0.1, 0.3]
    np.testing.assert_allclose(
        scores.threshold_at_fnr(fnr), scores_easy.threshold_at_fnr(fnr)
    )

    topr = [0.7, 0.8, 0.9, 0.912]
    np.testing.assert_allclose(
        scores.threshold_at_topr(topr), scores_easy.threshold_at_topr(topr)
    )


def test_threshold_setting_easy_neg():
    """Testing threshold setting in the presence of easy negative samples."""
    scores = Scores(pos=[], neg=range(100), score_class="neg")
    scores_easy = Scores(pos=[], neg=range(60), nb_easy_neg=40, score_class="neg")

    tnr = [0.7, 0.8, 0.9, 0.912]
    np.testing.assert_allclose(
        scores.threshold_at_tnr(tnr), scores_easy.threshold_at_tnr(tnr)
    )

    fpr = [0.02, 0.045, 0.1, 0.3]
    np.testing.assert_allclose(
        scores.threshold_at_fpr(fpr), scores_easy.threshold_at_fpr(fpr)
    )

    tonr = [0.7, 0.8, 0.9, 0.912]
    np.testing.assert_allclose(
        scores.threshold_at_tonr(tonr), scores_easy.threshold_at_tonr(tonr)
    )


@pytest.mark.parametrize(
    "pos, neg, score_class, expected_threshold, expected_eer",
    [
        [[0, 1, 1, 1], [0, 1, 1, 1], "pos", 1.0, 0.375],
        # Perfect separation
        [[2, 3, 4], [0, 1], "pos", 1.5, 0.0],
        [[0, 1], [3, 4], "neg", 2.0, 0.0],
        # Perfect separation, but in the wrong direction
        [[2, 3, 4], [5, 6], "pos", 4.5, 1.0],
        [[5, 6], [1, 2], "neg", 3.5, 1.0],
    ],
)
def test_eer(pos, neg, score_class, expected_threshold, expected_eer):
    scores = Scores(pos, neg, score_class=score_class)
    threshold, eer = scores.eer()
    np.testing.assert_allclose(threshold, expected_threshold)
    np.testing.assert_allclose(eer, expected_eer)


def test_easy_edgecase_eer():
    """Tests case where due to the presence of easy samples we cannot compute EER."""
    scores = Scores(pos=[0, 1], neg=[2, 3], nb_easy_pos=1)
    threshold, eer = scores.eer()
    np.testing.assert_allclose(threshold, 2.0)
    np.testing.assert_allclose(eer, 2.0 / 3.0)

    scores = Scores(pos=[0, 1], neg=[2, 3], nb_easy_neg=1)
    threshold, eer = scores.eer()
    np.testing.assert_allclose(threshold, 1.0)
    np.testing.assert_allclose(eer, 2.0 / 3.0)


def test_find_root_invalid_input():
    # Tests raising exception on invalid input function.
    with pytest.raises(ValueError):
        Scores._find_root(lambda _: 1.0, 0.0, 1.0, True)


#
def test_bootstrap_sample_replacement():
    scores = Scores(
        pos=[1, 2, 3, 4], neg=[1, 2, 3], score_class="neg", equal_class="neg"
    )

    with pytest.raises(ValueError):
        scores.bootstrap_sample(method="no_such_method")

    sample = scores.bootstrap_sample(method="replacement")
    assert sample.pos.size == scores.pos.size
    assert sample.neg.size == scores.neg.size
    assert set(sample.pos).issubset(set(scores.pos))
    assert set(sample.neg).issubset(set(scores.neg))
    assert sample.score_class == scores.score_class
    assert sample.equal_class == scores.equal_class


def test_bootstrap_sample_proportion():
    scores = Scores(pos=[1, 2, 3, 4, 5, 6], neg=[1, 2, 3, 4])

    with pytest.raises(ValueError):
        scores.bootstrap_sample(method="proportion", ratio=None)

    sample = scores.bootstrap_sample(method="proportion", ratio=0.5)
    assert sample.pos.size == 3
    assert sample.neg.size == 2
    assert set(sample.pos).issubset(set(scores.pos))
    assert set(sample.neg).issubset(set(scores.neg))


def test_bootstrap_sample_callable():
    scores = Scores(pos=[1, 2, 3, 4], neg=[1, 2, 3])

    with pytest.raises(ValueError):
        scores.bootstrap_sample(method=None)

    sample = scores.bootstrap_sample(lambda x: x)  # Identity sampling
    assert sample == scores


@pytest.mark.parametrize("metric", ["eer", Scores.eer])
@pytest.mark.parametrize("nb_samples", [1, 3])
def test_bootstrap_metric(metric, nb_samples):
    scores = Scores(pos=[1, 2, 3, 4], neg=[1, 2, 3])
    samples = scores.bootstrap_metric(metric, nb_samples=nb_samples)
    assert samples.shape == (nb_samples, 2)


def test_bootstrap_ci_identity():
    scores = Scores(pos=[1, 2, 3, 4], neg=[1, 2, 3])
    nb_samples = 3
    # Testing with identity sampling, in which case CI should collapse
    ci = scores.bootstrap_ci(
        metric="eer", nb_samples=nb_samples, sampling_method=lambda x: x
    )
    eer = scores.eer()
    for j in range(nb_samples):
        np.testing.assert_equal(ci[..., 0], eer)
        np.testing.assert_equal(ci[..., 1], eer)

    # Test invalid bootstrap method
    with pytest.raises(ValueError):
        scores.bootstrap_ci(metric="eer", bootstrap_method="no_such_method")


@pytest.mark.parametrize("bootstrap_method", ["quantile", "bc", "bca"])
def test_bootstrap_ci_gaussian(bootstrap_method):
    rng = np.random.default_rng(seed=42)
    nb_inside = 0
    for j in range(100):
        scores = Scores(pos=rng.normal(size=100), neg=[])
        ci = scores.bootstrap_ci(
            metric=lambda s: np.mean(s.pos),
            bootstrap_method=bootstrap_method,
            # We use a custom sampling method to make the test deterministic by fixing
            # the random number generator
            sampling_method=lambda s: Scores(
                pos=rng.choice(s.pos, size=s.pos.size, replace=True), neg=[]
            ),
            nb_samples=200,
        )
        nb_inside += ci[0] < 0 < ci[1]
    # If the test starts failing, we should check if it is due to flakiness of the RNG.
    # There is a balance between accuracy and how long the tests take to run.
    assert 92 < nb_inside < 98


def test_pointwise_cm():
    cm = pointwise_cm(
        labels=[1, 1, 0, 0],
        scores=[1, 0, 1, 0],
        threshold=1.0,
        score_class="pos",
        equal_class="pos",
    )
    assert cm.shape == (4, 2, 2)
    np.testing.assert_equal(cm[0], [[1, 0], [0, 0]])
    np.testing.assert_equal(cm[1], [[0, 1], [0, 0]])
    np.testing.assert_equal(cm[2], [[0, 0], [1, 0]])
    np.testing.assert_equal(cm[3], [[0, 0], [0, 1]])

    cm = pointwise_cm(
        labels=[1, 1, 0, 0],
        scores=[1, 0, 1, 0],
        threshold=0.0,
        score_class="pos",
        equal_class="neg",
    )
    np.testing.assert_equal(cm[0], [[1, 0], [0, 0]])
    np.testing.assert_equal(cm[1], [[0, 1], [0, 0]])
    np.testing.assert_equal(cm[2], [[0, 0], [1, 0]])
    np.testing.assert_equal(cm[3], [[0, 0], [0, 1]])

    cm = pointwise_cm(
        labels=[1, 1, 0, 0],
        scores=[1, 0, 1, 0],
        threshold=0.0,
        score_class="neg",
        equal_class="pos",
    )
    np.testing.assert_equal(cm[0], [[0, 1], [0, 0]])
    np.testing.assert_equal(cm[1], [[1, 0], [0, 0]])
    np.testing.assert_equal(cm[2], [[0, 0], [0, 1]])
    np.testing.assert_equal(cm[3], [[0, 0], [1, 0]])

    cm = pointwise_cm(
        labels=[1, 1, 0, 0],
        scores=[1, 0, 1, 0],
        threshold=1.0,
        score_class="neg",
        equal_class="neg",
    )
    np.testing.assert_equal(cm[0], [[0, 1], [0, 0]])
    np.testing.assert_equal(cm[1], [[1, 0], [0, 0]])
    np.testing.assert_equal(cm[2], [[0, 0], [0, 1]])
    np.testing.assert_equal(cm[3], [[0, 0], [1, 0]])


def test_pointwise_cm_shape():
    cm = pointwise_cm(
        labels=np.zeros((3, 4)), scores=np.zeros((3, 4)), threshold=np.zeros((5, 1))
    )
    assert cm.shape == (3, 4, 5, 1, 2, 2)


@pytest.mark.parametrize(
    "original, alias, args",
    [
        [Scores.tpr, Scores.tar, (2,)],
        [Scores.fnr, Scores.frr, (2,)],
        [Scores.tnr, Scores.trr, (2,)],
        [Scores.fpr, Scores.far, (2,)],
        [Scores.threshold_at_tpr, Scores.threshold_at_tar, (0.3,)],
        [Scores.threshold_at_fnr, Scores.threshold_at_frr, (0.3,)],
        [Scores.threshold_at_tnr, Scores.threshold_at_trr, (0.3,)],
        [Scores.threshold_at_fpr, Scores.threshold_at_far, (0.3,)],
        [Scores.threshold_at_topr, Scores.threshold_at_acceptance_rate, (0.3,)],
        [Scores.threshold_at_tonr, Scores.threshold_at_rejection_rate, (0.3,)],
    ],
)
def test_aliases(original, alias, args):
    scores = Scores(pos=[1, 2, 3, 4, 5, 6], neg=[0.2, 1.2, 1.3, 3, 4, 4, 4])
    np.testing.assert_equal(original(scores, *args), alias(scores, *args))


@pytest.mark.parametrize(
    "target, metric, points, expected",
    [
        [0.5, "topr", None, 4],
        [0.5, Scores.topr, None, 4],
        [0.5, Scores.topr, [0, 1], 1],
        [0.5, Scores.topr, 2, 4.0],
    ],
)
def test_threshold_at_metric(target, metric, points, expected):
    scores = Scores(pos=[0, 1, 2, 3], neg=[4, 5, 6, 7])
    result = scores.threshold_at_metric(target=target, metric=metric, points=points)
    np.testing.assert_equal(result, expected)


def test_threshold_at_metrics_not_enough_scores():
    with pytest.raises(ValueError):
        scores = Scores(pos=[1], neg=[])
        scores.threshold_at_metric(0.2, "fpr", None)

    with pytest.raises(ValueError):
        scores = Scores(pos=[], neg=[1])
        scores.threshold_at_metric(0.2, "fpr", 10)


@pytest.mark.parametrize(
    "pos, neg, targets",
    [
        [[1, 2, 3, 4], [1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1]],
        [[0, 1], [0, 1], 0.6],
        [[0, 1], [0, 1], -0.1],
        [[0, 1], [0, 1], 1.1],
    ],
)
def test_consistency_of_thresholds(pos, neg, targets):
    scores = Scores(pos=pos, neg=neg)
    thresholds_at_tpr = scores.threshold_at_tpr(targets)
    thresholds_at_metric_tpr = scores.threshold_at_metric(
        target=targets, metric=Scores.tpr, points=None
    )
    # reshape and concatenate
    thresholds_at_metric_tpr = np.concatenate(
        [threshold.reshape(-1) for threshold in thresholds_at_metric_tpr]
    )
    np.testing.assert_array_almost_equal(thresholds_at_tpr, thresholds_at_metric_tpr)
