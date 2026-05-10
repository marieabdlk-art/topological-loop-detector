import numpy as np
from topoloop.topology import h1_diagram, encode_h1_profile

def test_h1_profile_keys():
    th = np.linspace(0, 2*np.pi, 64)
    xy = np.c_[np.cos(th), np.sin(th)]
    profile = encode_h1_profile(h1_diagram(xy), xy)
    assert "topo_max" in profile
    assert "n_bars_tau" in profile
    assert "topo_top2_sum" in profile
