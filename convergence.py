import numpy as np

def l2convergency(x,y):
    return 2 - (x + y) * 10

def w2convergency(x,y):
    return 1 - (x - y)

def convtrue(x,y):
    return (np.log(x) - np.log(y)) / np.log(2)

print(l2convergency(0.00020387945778997126, 8.696220406567263e-05))
print(l2convergency(8.696220406567263e-05, 4.7759939230333205e-05))
print(w2convergency(0.10345234565273223, 0.06056155344767739))
print(w2convergency(0.06056155344767739, 0.0416301635876717))
