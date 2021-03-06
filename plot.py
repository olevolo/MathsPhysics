def compare(plt, A, B):
    ax1 = plt.subplot(121, aspect='equal')
    _plot(ax1, **A)
    ax2 = plt.subplot(122, sharex=ax1, sharey=ax1)
    _plot(ax2, **B)


def plot(plt, A):
    ax = plt.subplot(111)
    _plot(ax, **A)


def _plot(ax, **kw):
    vertices(ax, **kw)
    ax.axes.set_aspect('equal')

    if 'segments' in kw: segments(ax, **kw)
    if 'triangles' in kw: triangles(ax, **kw)
    if 'holes' in kw: holes(ax, **kw)
    if 'edges' in kw: edges(ax, **kw)

    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)


def vertices(ax, **kw):
    verts = kw['vertices']
    ax.scatter(*verts.T, color='k')
    if 'labels' in kw:
        for i in range(verts.shape[0]):
            ax.annotate(str(i), (verts[i, 0] + 0.01, verts[i, 1] + 0.02) , fontsize=10, color='red')
    if 'markers' in kw:
        vm = kw['vertex_markers']
        for i in range(verts.shape[0]):
            ax.text(verts[i, 0], verts[i, 1], str(vm[i]))


def segments(ax, **kw):
    verts = kw['vertices']
    segs = kw['segments']
    for beg, end in segs:
        x0, y0 = verts[beg, :]
        x1, y1 = verts[end, :]
        ax.fill([x0, x1], [y0, y1], color='k', linestyle='-', linewidth=1)


def _number_triangle(ax, triangle, vertices, number):
    xs = [vertices[i][0] for i in triangle]
    print(xs)

    ys = [vertices[i][1] for i in triangle]
    print(ys)

    avg_x = sum(xs) / len(xs)
    avg_y = sum(ys) / len(ys)

    ax.annotate(str(number), (avg_x, avg_y))

    #min_x = min(xs)
    #max_x = max(xs)
    #min_y = min(ys)
    #max_y = max(ys)
    #ax.annotate(str(number), ((min_x+max_x)/2, (min_y+max_y)/2))



def triangles(ax, **kw):
    verts = kw['vertices']
    ax.triplot(verts[:, 0], verts[:, 1], kw['triangles'], marker='o', color='k', linestyle='-', linewidth=1)
    if kw.get('number_triangles'):
        for i, triangle in enumerate(kw['triangles']):
            _number_triangle(ax, triangle, verts, i)


def holes(ax, **kw):
    ax.scatter(*kw['holes'].T, marker='x', color='r')


def edges(ax, **kw):
    """
    Plot regular edges and rays (edges whose one endpoint is at infinity)
    """
    verts = kw['vertices']
    edges = kw['edges']
    for beg, end in edges:
        x0, y0 = verts[beg, :]
        x1, y1 = verts[end, :]
        ax.fill([x0, x1], [y0, y1], facecolor='none', edgecolor='k', linewidth=.5)

    if ('ray_origins' not in kw) or ('ray_directions' not in kw):
        return

    lim = ax.axis()
    ray_origin = kw['ray_origins']
    ray_direct = kw['ray_directions']
    for (beg, (vx, vy)) in zip(ray_origin.flatten(), ray_direct):
        x0, y0 = verts[beg, :]
        scale = 100.0  # some large number
        x1, y1 = x0 + scale * vx, y0 + scale * vy
        ax.fill([x0, x1], [y0, y1], facecolor='none', edgecolor='k', linewidth=.5)
    ax.axis(lim)  # make sure figure is not rescaled by ifinite ray
