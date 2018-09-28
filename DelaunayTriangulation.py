import numpy as np
import triangle
from helpers import is_between


class DelaunayTriangulation:
    def __init__(self, **kwargs):
        self.min_angle = kwargs['min_angle']
        self.max_area = kwargs['max_area']
        self.label_vertices = kwargs.get('label_vertices')
        self.label_triangles = kwargs.get('label_triangles')
        self.triangulation_params = {
            'vertices': np.array([(point['x'], point['y']) for point in kwargs['points']]),
            'segments': np.array([[i, (i+1) % len(kwargs['points'])] for i in range(len(kwargs['points']))])
        }
        if 'holes' in kwargs:
            self.triangulation_params['holes'] = np.array(kwargs['holes'])
        self.triangulated = None
        self.triangulated_info = None

    def triangulate(self):
        self.triangulated = triangle.triangulate(self.triangulation_params, f'pq{self.min_angle}a{self.max_area}')

        if self.label_vertices:
            self.triangulated['labels'] = self.label_vertices
        if self.label_triangles:
            self.triangulated['number_triangles'] = self.label_triangles

        raw_info = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in self.triangulated.items()}

        boundary_points_dict = {
            tuple(segment): self._boundary_segments(segment, self.triangulated['vertices'])
            for segment in self.triangulation_params['segments']
        }

        for segment, points in boundary_points_dict.items():
            x1, x2 = self.triangulated['vertices'][segment[0]][0], self.triangulated['vertices'][segment[1]][0]
            y1, y2 = self.triangulated['vertices'][segment[0]][1], self.triangulated['vertices'][segment[1]][1]

            if x1 < x2:
                boundary_points_dict[segment] = sorted(points, key=self._take_x)
            elif x2 < x1:
                boundary_points_dict[segment] = sorted(points, key=self._take_x, reverse=True)
            elif y1 < y2:
                boundary_points_dict[segment] = sorted(points, key=self._take_y)
            else:
                boundary_points_dict[segment] = sorted(points, key=self._take_y, reverse=True)

        for segment, points in boundary_points_dict.items():
            boundary_points_dict[segment] = [[boundary_points_dict[segment][i], boundary_points_dict[segment][(i + 1)]]
                                             for i in range(len(points) - 1)]
        self.triangulated_info = {
            'CT': raw_info['vertices'],
            'NT': raw_info['triangles'],
            'NTG': boundary_points_dict
        }

    def _boundary_segments(self, parent_segment, vertices):
        a, b = vertices[parent_segment[0]][0], vertices[parent_segment[1]][0]
        c, d = vertices[parent_segment[0]][1], vertices[parent_segment[1]][1]
        a, b = (a, b) if a < b else (b, a)
        c, d = (c, d) if c < d else (d, c)
        suspicious_points = []
        for i in range(len(vertices)):
            if a <= vertices[i][0] <= b and c <= vertices[i][1] <= d:
                suspicious_points.append(i)

        segment_points = []
        for i in suspicious_points:
            if is_between(vertices[parent_segment[0]], vertices[i], vertices[parent_segment[1]]):
                segment_points.append(i)
        return segment_points

    def _take_x(self, element):
        return self.triangulated['vertices'][element][0]

    def _take_y(self, element):
        return self.triangulated['vertices'][element][1]
