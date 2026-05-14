from topoloop.benchmark import run_single_benchmark, feature_sets
from topoloop.features import BASELINE_COLS


def test_feature_sets_include_geometry_only():
    sets = feature_sets(k_bars=8)
    assert "geometry_only" in sets
    assert sets["geometry_only"] == BASELINE_COLS


def test_single_benchmark_runs_small():
    out = run_single_benchmark(seed=0, n_per_regime=1, window_size=32, stride=8)
    assert "summary" in out
    assert "per_regime" in out
    assert "trigger_df" in out
    assert "geometry_accuracy" in out["summary"].columns


def test_trigger_outputs_expected_columns():
    out = run_single_benchmark(seed=1, n_per_regime=1, window_size=32, stride=8)
    trigger_df = out["trigger_df"]
    assert "generic_alerted" in trigger_df.columns
    assert "vnext1_gated_alerted" in trigger_df.columns
    assert "generic_correct" in trigger_df.columns
    assert "vnext1_gated_correct" in trigger_df.columns
