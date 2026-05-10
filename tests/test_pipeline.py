from topoloop.generators import make_dataset
from topoloop.features import build_window_table, add_temporal_features, add_rejection_flags_vnext1

def test_window_pipeline_runs():
    data = make_dataset(n_per_regime=1, seed=0)
    feat = build_window_table(data, window_size=32, stride=8)
    feat = add_temporal_features(feat)
    feat = add_rejection_flags_vnext1(feat)
    assert "topo_max" in feat.columns
    assert "current_h1_streak" in feat.columns
    assert "reject_transient" in feat.columns
