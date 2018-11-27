from helpers import tri_area, distance
import numpy as np

class FemSolver:
    def __init__(self, triangulated_info, conds):
        self.triangulated_info = triangulated_info
        self.conds = conds
        self.element_matrices = None
        self.boundary_matrices = None
        self.num_points = len(self.triangulated_info['CT'])
        self.K = np.zeros((self.num_points, self.num_points))
        self.Q = np.zeros((self.num_points, 1))
        self.F = np.zeros((self.num_points, 1))

    def form_SofLE(self):
        for element_key in self.element_matrices:
            mapping_element_vertices = self.triangulated_info['NT'][int(element_key)]
            Ke = self.element_matrices[element_key]['Ke']
            Me = self.element_matrices[element_key]['Me']
            Qe = self.element_matrices[element_key]['Qe']

            for i in range(3):
                for j in range(3):
                    self.K[mapping_element_vertices[i], mapping_element_vertices[j]] += Ke[i, j] + Me[i, j]
                self.F[mapping_element_vertices[i], 0] += Qe[i, 0]

        for boundary in self.boundary_matrices:
            Be = self.boundary_matrices[boundary]['Be']
            Ce = self.boundary_matrices[boundary]['Ce']
            for i in range(2):
                for j in range(2):
                    self.K[boundary[i], boundary[j]] += Be[i, j]
                self.F[boundary[i], 0] += Ce[i, 0]


    def prepare_matrices(self):
        self.element_matrices = {}
        for idx, triangle in enumerate(self.triangulated_info['NT']):
            triangle = [self.triangulated_info['CT'][i] for i in triangle]
            self.element_matrices[str(idx)] = {
                'Ke': self._get_Ke(triangle),
                'Me': self._get_Me(triangle),
                'Qe': self._get_Qe(triangle)
            }

        self.boundary_matrices = {}
        for boundary_key in self.triangulated_info['NTG']:
            for side in self.triangulated_info['NTG'][boundary_key]:
                self.boundary_matrices[tuple(side)] = {
                    'Be': self._get_Be([self.triangulated_info['CT'][i] for i in side], boundary_key),
                    'Ce': self._get_Ce([self.triangulated_info['CT'][i] for i in side], boundary_key)
                }

    def _get_Ke(self, triangle):
        delta = 2 * tri_area(triangle)
        a11 = self.conds['a11']
        a22 = self.conds['a22']
        coeffs = np.vstack((self._get_coeffs(triangle, 0),
                           self._get_coeffs(triangle, 1),
                           self._get_coeffs(triangle, 2)))

        b = coeffs[:,1].reshape(3,1)
        c = coeffs[:,2].reshape(3,1)

        return (np.dot(b,b.T) * a11 + np.dot(c,c.T) * a22) / (2*delta)

    def _get_coeffs(self, triangle, idx):
        i = idx % 3
        j = (idx + 1) % 3
        m = (idx + 2) % 3
        a = triangle[j][0] * triangle[m][1] - triangle[j][1]*triangle[m][0]
        b = triangle[j][1] - triangle[m][1]
        c = triangle[m][0] - triangle[j][0]
        return np.array([a, b, c])


    def _get_Me(self, triangle):
        delta = 2 * tri_area(triangle)
        d = self.conds['d']
        return np.array(
            [
                [2, 1, 1],
                [1, 2, 1],
                [1, 1, 2]
            ]) * d * delta / 24

    def _get_Qe(self, triangle):
        delta = 2 * tri_area(triangle)
        f = self.conds['f']
        return np.dot(
            np.array(
                [
                    [2, 1, 1],
                    [1, 2, 1],
                    [1, 1, 2]
                ]
            ),
            np.array(
                [
                    [1],
                    [1],
                    [1]
                ]
            ) * f
        ) * delta / 24


    def _get_Be(self, side, boundary):
        sigma = self.conds[boundary]['Sigma']
        beta = self.conds[boundary]['Beta']
        gamma = distance(side[0], side[1])
        return -np.array(
            [
                [2,1],
                [1,2]
            ]
        ) * sigma * gamma / (beta * 6)


    def _get_Ce(self, side, boundary):
        sigma = self.conds[boundary]['Sigma']
        beta = self.conds[boundary]['Beta']
        gamma = distance(side[0], side[1])
        Uc = self.conds[boundary]['Uc']

        return np.array(
            [
                [1],
                [1]
            ]
        ) * sigma * gamma * Uc / (beta * 2)
