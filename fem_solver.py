from helpers import tri_area, distance
import numpy as np

class FemSolver:
    def __init__(self, triangulated_info, conds):
        self.triangulated_info = triangulated_info
        self.conds = conds
        self.element_matrices = None

    def prepare_matrices(self):
        self.element_matrices = {}
        for idx, triangle in enumerate(self.triangulated_info['NT']):
            Be = np.zeros((2,2))
            Ce = np.zeros((2, 1))

            sides = [[triangle[0],triangle[1]], [triangle[1], triangle[2]],[triangle[2], triangle[0]]]
            triangle = [self.triangulated_info['CT'][i] for i in triangle]
            for side in sides:
                for boundary in self.triangulated_info['NTG']:
                    if side in self.triangulated_info['NTG'][boundary]:
                        Be += self._get_Be(triangle, [self.triangulated_info['CT'][i] for i in side], boundary)
                        Ce += self._get_Ce(triangle, [self.triangulated_info['CT'][i] for i in side], boundary)

            Ke = self._get_Ke(triangle)
            Me = self._get_Me(triangle)
            Qe = self._get_Qe(triangle)

            tri_matrices = {}
            tri_matrices['Ke'] = Ke
            tri_matrices['Me'] = Me
            tri_matrices['Qe'] = Qe
            tri_matrices['Be'] = Be
            tri_matrices['Ce'] = Ce

            self.element_matrices[str(idx)] = tri_matrices

    def _get_Ke(self, triangle):
        delta = tri_area(triangle)
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
        delta = tri_area(triangle)
        d = self.conds['d']
        return np.array(
            [
                [2, 1, 1],
                [1, 2, 1],
                [1, 1, 2]
            ]) * d * delta / 24

    def _get_Qe(self, triangle):
        delta = tri_area(triangle)
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


    def _get_Be(self, triangle, side, boundary):
        sigma = self.conds[boundary]['Sigma']
        beta = self.conds[boundary]['Beta']
        gamma = distance(side[0], side[1])
        return -np.array(
            [
                [2,1],
                [1,2]
            ]
        ) * sigma * gamma / (beta * 6)


    def _get_Ce(self,triangle, side, boundary):
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
