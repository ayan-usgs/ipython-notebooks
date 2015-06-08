from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib as mpl
import numpy as np
import pyproj


def quiver_response(lon,
                    lat,
                    dx,
                    dy,
                    height,
                    width,
                    # request,
                    unit_vectors=False,
                    dpi=80):

    # bbox = request.GET['bbox']
    # width = request.GET['width']
    # height = request.GET['height']
    # colormap = request.GET['colormap']
    # colorscalerange = request.GET['colorscalerange']
    # cmin = colorscalerange.min
    # cmax = colorscalerange.max
    colormap = None
    cmin = None
    cmax = None
    # crs = request.GET['crs']

    # EPSG4326 = pyproj.Proj(init='EPSG:4326')
    # x, y = pyproj.transform(EPSG4326, crs, lon, lat)  # TODO order for non-inverse?

    fig = Figure(dpi=dpi, facecolor='none', edgecolor='none')
    fig.set_alpha(0)
    fig.set_figheight(height/dpi)
    fig.set_figwidth(width/dpi)

    ax = fig.add_axes([0., 0., 1., 1.], xticks=[], yticks=[])
    ax.set_axis_off()
    mags = np.sqrt(dx**2 + dy**2)

    cmap = mpl.cm.get_cmap(colormap)
    # Set out of bound data to NaN so it shows transparent?
    # Set to black like ncWMS?
    # Configurable by user?
    norm = None
    if cmin and cmax:
        mags[mags > cmax] = cmax
        mags[mags < cmin] = cmin
        bounds = np.linspace(cmin, cmax, 15)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # plot unit vectors
    if unit_vectors:
        ax.quiver(lon, lat, dx/mags, dy/mags, mags, cmap=cmap)
    else:
        ax.quiver(lon, lat, dx, dy, mags, cmap=cmap, norm=norm)
        
    x_min = np.min(lon)
    x_max = np.max(lon)
    y_min = np.min(lat)
    y_max = np.max(lat)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_min)
    ax.set_frame_on(False)
    ax.set_clip_on(False)
    ax.set_position([0., 0., 1., 1.])

    canvas = FigureCanvasAgg(fig)
    # response = HttpResponse(content_type='image/png')
    # canvas.print_png(response)
    return canvas