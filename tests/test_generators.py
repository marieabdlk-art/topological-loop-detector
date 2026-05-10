from topoloop.generators import make_dataset, LOOP_REGIMES

def test_make_dataset_nonempty():
    data = make_dataset(n_per_regime=1, seed=0)
    assert len(data) > 0

def test_loop_labels():
    data = make_dataset(n_per_regime=1, seed=0)
    for tr in data.values():
        assert tr.label_loop == int(tr.regime in LOOP_REGIMES)
