import numpy as np

class MatrixFactorizationSGD:
    def __init__(self, n_factors=4, lr=0.01, reg=0.05, n_epochs=30):
        self.n_factors = n_factors
        self.lr = lr
        self.reg = reg
        self.n_epochs = n_epochs
        self.mu = 0.0
        self.b_u = None
        self.b_i = None
        self.P = None
        self.Q = None

    def fit(self, R_sparse):
        # TODO: Implement SGD matrix factorization with user and item biases
        pass

    def predict(self, u, i):
        # TODO: Compute predicted rating r_hat_{u,i}
        pass
