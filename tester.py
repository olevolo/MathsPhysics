import numpy as np

class Tester:
    def __init__(self, fem_solution, conds, triangulated_info):
        self.fem_solution = fem_solution
        self.conds = conds
        self.vertices = triangulated_info['CT']
        self.a = 2
        self.n = len(triangulated_info['CT'])
        self.exact_solution = self.calculate_exact_solution(self.vertices)


    def calculate_exact_solution(self, vertices):
        # hardcoded case from example
        exact_solution = []
        for i in range(0, len(vertices)):
            exact_solution.append(self.conds['f'] / self.conds['a11'] * vertices[i][0] / 2 * (self.a - vertices[i][0]))
        return exact_solution

    def get_abs_error_L2(self):
        print(len(self.exact_solution), " ", len(self.fem_solution), " ", self.n)
        return [np.abs(np.power(self.exact_solution[i] - self.fem_solution[i], 2)) for i in range(0, self.n)]
        #return np.sum(np.abs(np.power(self.exact_solution - self.fem_solution, 2)))


    def get_relative_error_L2(self):
        #return self.get_abs_error_L2() / np.sum(np.abs(np.power(self.fem_solution,2)))
        return np.sum(self.get_abs_error_L2()) / np.sum(np.abs(np.power(self.fem_solution, 2)))

    def get_abs_error_W2(self):
        return None

    def get_relative_error_W2(self):
        return None