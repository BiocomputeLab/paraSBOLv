import parasbolv as psv
import matplotlib.pyplot as plt

def test_plotting_glyph():
    """Test that a single glyph with parameters, style, and rotation can be plotted."""
    renderer = psv.GlyphRenderer()
    fig, ax = plt.subplots()
    ax.set_ylim([0,100])
    ax.set_xlim([0,100])
    user_parameters = {}
    user_parameters = {'arrowbody_height':15}
    cds_style = {}
    cds_style = {'cds':{'facecolor': (0,0,1), 'edgecolor': (1,1,0), 'linewidth': 10}}
    bounds, end_point = renderer.draw_glyph(ax,
                                            'CDS',
                                            (50,50),
                                            user_parameters=user_parameters,
                                            user_style = cds_style,
                                            rotation = 3.142/3)

def test_plotting_construct():
    """Test that a construct can be plotted."""
    renderer = psv.GlyphRenderer()
    fig, ax = plt.subplots()

    construct = psv.Construct([["RibosomeEntrySite", 'forward', None, None]],
                              renderer,
                              fig=fig,
                              ax=ax,
                              start_position=(0,0),
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

def test_plotting_interactions():
    """Test loading glyphs from SVGs with no errors/exceptions."""
    renderer = psv.GlyphRenderer()
    part_list = [["Promoter", 'forward', None, None],["Promoter", 'forward', None, None]]
    int_list = [[part_list[0], part_list[1], 'inhibition', {'color': (1,0,0),
                                                            'headheight': 13.0,
                                                            'headwidth': 14.0,
                                                            'zorder': 2,
                                                            'direction': 'forward',
                                                            'linewidth': 2.0,
                                                            'heightskew': 15.0,
                                                            'sending_length_skew': 3.0,
                                                            'receiving_length_skew': 4.0,
                                                            'distance_from_baseline': 27.0}]]
    construct = psv.Construct(part_list, renderer, interaction_list=int_list)
    fig, ax, baseline_start, baseline_end, bounds = construct.draw()
