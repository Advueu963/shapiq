"""This test module contains all tests regarding the SV stratified sampling approximator."""

from __future__ import annotations

import numpy as np
import pytest

from shapiq.approximator.marginals import OwenSamplingSV
from shapiq.games.benchmark import DummyGame


@pytest.mark.parametrize(
    ("n", "m", "expected"),
    [
        (5, 1, [0.5]),
        (5, 2, [0.0, 1.0]),
        (5, 3, [0.0, 0.5, 1.0]),
        (5, 4, [0.0, 0.33333, 0.66666, 1.0]),
        (5, 5, [0.0, 0.25, 0.5, 0.75, 1.0]),
        (5, 6, [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]),
        (5, 10, [0.0, 0.11111, 0.22222, 0.33333, 0.44444, 0.55555, 0.66666, 0.77777, 0.88888, 1.0]),
        (5, 11, [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]),
    ],
)
def test_anchorpoints(n, m, expected):
    """Tests the generation of anchor points in the OwenSamplingSV approximator."""
    approximator = OwenSamplingSV(n, m, random_state=42)
    output = approximator.get_anchor_points(m)
    expected = np.array(expected)
    assert np.allclose(output, expected)

    with pytest.raises(ValueError):
        _ = approximator.get_anchor_points(0)


@pytest.mark.parametrize(
    ("n", "m", "budget"),
    [
        (5, 3, 102),
        (5, 3, 100),
        (5, 3, 1000),
        (5, 1, 1000),
        (5, 2, 1000),
        (5, 10, 1000),
        (5, 41, 10000),
    ],
)
def test_approximate(n, m, budget):
    """Tests the approximation of the OwenSamplingSV approximator."""
    interaction = (1, 2)
    game = DummyGame(n, interaction)

    approximator = OwenSamplingSV(n, m, random_state=42)

    assert approximator.index == "SV"

    # test for init parameter
    assert approximator.index == "SV"
    assert approximator.n == n
    assert approximator.max_order == 1
    assert approximator.top_order is False

    sv_estimates = approximator.approximate(budget, game)

    # check that the budget is respected
    assert game.access_counter <= budget
    assert sv_estimates.index == "SV"
    assert sv_estimates.max_order == 1
    assert sv_estimates.min_order == 0
    assert sv_estimates.estimation_budget <= budget
    assert sv_estimates.estimated is True  # always estimated

    # check Shapley values for all players that have only marginal contributions of size 0.2
    # their estimates must be exactly 0.2
    assert sv_estimates[(0,)] == pytest.approx(0.2, 0.001)
    assert sv_estimates[(3,)] == pytest.approx(0.2, 0.001)
    assert sv_estimates[(4,)] == pytest.approx(0.2, 0.001)

    # check Shapley values for interaction players
    if budget >= 100000 and m >= 40:
        assert sv_estimates[(1,)] == pytest.approx(0.7, 0.1)
        assert sv_estimates[(2,)] == pytest.approx(0.7, 0.1)
