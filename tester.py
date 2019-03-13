import numpy as np

from fem_solver import FemSolver
from helpers import tri_area


class Tester:
    def __init__(self, fem_solution, conds, delaunay_triangulation, fem_solver): # triangulated_info
        self.fem_solution = fem_solution
        self.conds = conds
        self.vertices = delaunay_triangulation.triangulated_info['CT']
        self.a = 2
        self.n = len(delaunay_triangulation.triangulated_info['CT'])
        self.exact_solution = self.calculate_exact_solution(self.vertices)
        self.exact_derivatives = self.calculate_exact_derivatives(self.vertices)
        self.delaunay_triangulation = delaunay_triangulation
        self.vertex_derivatives = {}
        self.derivatives = np.zeros_like(self.fem_solution)
        self.fem_solver = fem_solver

    def calculate_exact_solution(self, vertices):
        # hardcoded case from example
        exact_solution = []
        for i in range(len(vertices)):
            exact_solution.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.a - vertices[i][0]))
        return exact_solution

    def get_exact_soluton(self):
        return self.exact_solution

    def get_abs_error_L2(self):
        # print(len(self.exact_solution), " ", len(self.fem_solution), " ", self.n)
        return [np.power(np.abs(self.exact_solution[i] - self.fem_solution[i]), 2) for i in range(0, self.n)]
        # return np.sum(np.abs(np.power(self.exact_solution - self.fem_solution, 2)))

    def get_relative_error_L2(self):
        # return self.get_abs_error_L2() / np.sum(np.abs(np.power(self.fem_solution,2)))
        return np.sum(self.get_abs_error_L2()) / np.sum(np.abs(np.power(self.fem_solution, 2)))

    def get_abs_error_W2(self):
        print(self.derivatives)
        return [self.get_abs_error_L2()[i] + np.power(np.abs(self.exact_derivatives[i] - self.derivatives[i]), 2)
                for i in range(0, self.n)]

    def get_relative_error_W2(self):
        return np.sum(self.get_abs_error_W2()) / ( np.sum(np.abs(np.power(self.fem_solution, 2))) +
                                                         np.sum(np.abs(np.power(self.derivatives, 2))) )

    def calculate_exact_derivatives(self, vertices):
        exact_derivatives = []
        for i in range(len(vertices)):
            exact_derivatives.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.a - vertices[i][0]))
        return exact_derivatives

    def derivative(self):
        for triangle in self.delaunay_triangulation.triangulated['triangles']:
            derivative = 0
            u_h = self.fem_solution[triangle]
            for i in range(len(triangle)):
                triangle_n = [self.delaunay_triangulation.triangulated_info['CT'][i] for i in triangle]
                a, b, c = self.fem_solver._get_coeffs(triangle_n, i)
                delta = 2 * tri_area(triangle_n)
                derivative += (b + c)*u_h[i, 0]
            derivative /= delta
            for point_idx in triangle:
                if str(point_idx) in self.vertex_derivatives:
                    self.vertex_derivatives[str(point_idx)].append(derivative)
                else:
                    self.vertex_derivatives[str(point_idx)] = [derivative]

        for k, v in self.vertex_derivatives.items():
            self.derivatives[int(k), 0] = np.average(np.array(v))

