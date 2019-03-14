import numpy as np
from helpers import tri_area


def f(c_f, c_a11, vertex, width):
    return -c_f / (c_a11 * 2) * vertex[0] * vertex[0] + c_f / 2 * width * vertex[0]


def f_x1(c_f, c_a11, vertex, width):
    return -c_f / (c_a11 * 2) * 2 * vertex[0] + c_f * width / 2


def f_x2(c_f, c_a11, vertex, width):
    return 0


class Tester:
    def __init__(self, fem_solution, conds, delaunay_triangulation, fem_solver, width=0, height=0):
        self.fem_solution = fem_solution
        self.conds = conds
        self.fem_solver = fem_solver
        self.delaunay_triangulation = delaunay_triangulation
        self.width = width
        self.height = height
        self.exact_solution = self.calculate_exact_solution()
        self.n = len(self.exact_solution)

    def calculate_exact_solution(self):
        # hardcoded case from example
        vertices = self.delaunay_triangulation.triangulated_info['CT']
        exact_solution = []
        for i in range(len(vertices)):
            exact_solution.append(f(self.conds['f'], self.conds['a11'], vertices[i], self.width))
            # exact_solution.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.width - vertices[i][0]))
        return np.array(exact_solution).reshape((len(exact_solution), 1))

    def calculate_exact_solution_x1(self):
        # hardcoded case from example
        vertices = self.delaunay_triangulation.triangulated_info['CT']
        exact_solution_x1 = []
        for i in range(len(vertices)):
            exact_solution_x1.append(f_x1(self.conds['f'], self.conds['a11'], vertices[i], self.width))
            # exact_solution.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.width - vertices[i][0]))
        return np.array(exact_solution_x1).reshape((len(exact_solution_x1), 1))

    def calculate_exact_solution_x2(self):
        # hardcoded case from example
        vertices = self.delaunay_triangulation.triangulated_info['CT']
        exact_solution_x2 = []
        for i in range(len(vertices)):
            exact_solution_x2.append(f_x2(self.conds['f'], self.conds['a11'], vertices[i], self.width))
            # exact_solution.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.width - vertices[i][0]))
        return np.array(exact_solution_x2).reshape((len(exact_solution_x2), 1))

    def get_abs_error_L2(self):
        n = len(self.fem_solution)
        return np.sum(np.abs(np.square(self.exact_solution - self.fem_solution))) / n

    def get_relative_error_L2(self):
        return self.get_abs_error_L2() / np.sum(np.abs(np.square(self.exact_solution)))

    def get_abs_error_W2(self):
        n = len(self.fem_solution)
        df_x1_exact = self.calculate_exact_solution_x1()
        df_x2_exact = self.calculate_exact_solution_x2()
        df_x1_approx, df_x2_approx = self.calculate_derivatives()
        return np.sum(np.abs(np.square(self.exact_solution - self.fem_solution))) / n + \
               np.sum(np.abs(np.square(df_x1_exact - df_x1_approx))) / n + \
               np.sum(np.abs(np.square(df_x2_exact - df_x2_approx))) / n     # can cheat here

    def get_relative_error_W2(self):
        df_x1_exact = self.calculate_exact_solution_x1()
        df_x2_exact = self.calculate_exact_solution_x2()
        return self.get_abs_error_W2() / np.sum(np.square(self.exact_solution) + np.square(df_x1_exact) + np.square(df_x2_exact))

    def calculate_derivatives(self):
        vertex_derivatives = {}
        derivatives_x1 = np.zeros_like(self.fem_solution)
        derivatives_x2 = np.zeros_like(self.fem_solution)
        for triangle in self.delaunay_triangulation.triangulated['triangles']:
            derivative_x1 = 0
            derivative_x2 = 0
            u_h = self.fem_solution[triangle]
            for i in range(len(triangle)):
                triangle_n = [self.delaunay_triangulation.triangulated_info['CT'][i] for i in triangle]
                a, b, c = self.fem_solver._get_coeffs(triangle_n, i)
                delta = 2 * tri_area(triangle_n)
                derivative_x1 += b * u_h[i, 0]
                derivative_x2 += c * u_h[i, 0]
            derivative_x1 /= delta
            derivative_x2 /= delta
            for point_idx in triangle:
                if str(point_idx) in vertex_derivatives:
                    vertex_derivatives[str(point_idx)][0].append(derivative_x1)
                    vertex_derivatives[str(point_idx)][1].append(derivative_x2)
                else:
                    vertex_derivatives[str(point_idx)] = [[derivative_x1], [derivative_x2]]

        for k, v in vertex_derivatives.items():
            derivatives_x1[int(k), 0] = np.average(np.array(v[0]))
            derivatives_x2[int(k), 0] = np.average(np.array(v[1]))

        return derivatives_x1, derivatives_x2

