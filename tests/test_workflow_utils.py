import pytest

from workflow.utils import _normalize_frequency_dispersion_mode


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "numerical"),
        ("numerical", "numerical"),
        ("fd", "numerical"),
        ("energy", "energy"),
        ("energy_only", "energy"),
        ("none", "none"),
        ("off", "none"),
    ],
)
def test_normalize_frequency_dispersion_mode(value, expected):
    assert _normalize_frequency_dispersion_mode(value) == expected


def test_normalize_frequency_dispersion_mode_rejects_unknown():
    with pytest.raises(ValueError):
        _normalize_frequency_dispersion_mode("analytic")
