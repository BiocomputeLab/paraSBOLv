import parasbolv as psv
import matplotlib.pyplot as plt


def test_plotting_works():
    """Test that we cna plot a glyph without an error or exception being raised"""
    renderer = psv.GlyphRenderer()

    # Reused variables
    start_position = (0, 0)
    fig, ax = plt.subplots()

    construct = psv.Construct([["RibosomeEntrySite", None, None]],
                              renderer,
                              fig=fig,
                              ax=ax,
                              start_position=start_position,
                              gapsize=20,
                              padding=10)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()

    ax.plot([baseline_start[0], baseline_end[0]],
            [baseline_start[1], baseline_end[1]],
            color=(0, 0, 0), linewidth=1.5, zorder=0)


def test_find_bound_of_bounds():
    bounds = [
        [[1, 2], [3, 4]],
        [[5, 6], [7, 8]],

    ]

    assert psv.find_bound_of_bounds(bounds) == [(1, 2), (7, 8)]
