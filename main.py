import triangle
import triangle.plot
import numpy as np
import matplotlib.pyplot as plt

A = dict(vertices=np.array(((0,0), (1,0), (1, 1), (0, 1))))
B = triangle.triangulate(A)
triangle.plot.compare(plt, A, B)
plt.show()