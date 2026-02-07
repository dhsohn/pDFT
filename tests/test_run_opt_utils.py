from types import SimpleNamespace

import pytest

from run_opt_utils import (
    is_ts_quality_enforced,
    normalize_constraints,
    normalize_solvent_key,
)


def test_normalize_solvent_key_removes_non_alnum():
    assert normalize_solvent_key("N,N-dimethylformamide") == "nndimethylformamide"


def test_is_ts_quality_enforced_prefers_attribute():
    ts_quality = SimpleNamespace(enforce=False, to_dict=lambda: {"enforce": True})
    assert is_ts_quality_enforced(ts_quality) is False


def test_is_ts_quality_enforced_reads_dict_payload():
    assert is_ts_quality_enforced({"enforce": True}) is True
    assert is_ts_quality_enforced({"enforce": None}) is False


def test_normalize_constraints_builds_normalized_entries():
    bonds, angles, dihedrals = normalize_constraints(
        {
            "bonds": [{"i": 0, "j": 1, "length": 1.1}],
            "angles": [{"i": 0, "j": 1, "k": 2, "angle": 109.5}],
            "dihedrals": [{"i": 0, "j": 1, "k": 2, "l": 3, "dihedral": 180.0}],
        },
        atom_count=4,
    )
    assert bonds == [(0, 1, 1.1)]
    assert angles == [(0, 1, 2, 109.5)]
    assert dihedrals == [(0, 1, 2, 3, 180.0)]


def test_normalize_constraints_runtime_reports_out_of_range():
    with pytest.raises(
        ValueError,
        match=(
            r"constraints\.bonds\[0\]\.j index 3 is out of range for 3 atoms\."
        ),
    ):
        normalize_constraints(
            {"bonds": [{"i": 0, "j": 3, "length": 1.1}]},
            atom_count=3,
        )
