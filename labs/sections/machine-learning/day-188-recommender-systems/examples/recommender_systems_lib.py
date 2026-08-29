import numpy as np

class MatrixFactorizationSGD:
    def __init__(self, n_factors=4, lr=0.01, reg=0.05, n_epochs=30, random_state=42):
        self.n_factors = n_factors
        self.lr = lr
        self.reg = reg
        self.n_epochs = n_epochs
        self.random_state = random_state
        self.mu = 0.0
        self.b_u = None
        self.b_i = None
        self.P = None
        self.Q = None

    def fit(self, R_sparse):
        rng = np.random.default_rng(self.random_state)
        n_users = max(u for u, i, r in R_sparse) + 1
        n_items = max(i for u, i, r in R_sparse) + 1

        self.mu = np.mean([r for u, i, r in R_sparse])
        self.b_u = np.zeros(n_users)
        self.b_i = np.zeros(n_items)
        self.P = rng.normal(0, 0.1, (n_users, self.n_factors))
        self.Q = rng.normal(0, 0.1, (n_items, self.n_factors))

        for epoch in range(self.n_epochs):
            for u, i, r in R_sparse:
                pred = self.mu + self.b_u[u] + self.b_i[i] + np.dot(self.P[u], self.Q[i])
                err = r - pred

                self.b_u[u] += self.lr * (err - self.reg * self.b_u[u])
                self.b_i[i] += self.lr * (err - self.reg * self.b_i[i])

                p_old = self.P[u].copy()
                self.P[u] += self.lr * (err * self.Q[i] - self.reg * self.P[u])
                self.Q[i] += self.lr * (err * p_old - self.reg * self.Q[i])

        return self

    def predict(self, u, i):
        return float(self.mu + self.b_u[u] + self.b_i[i] + np.dot(self.P[u], self.Q[i]))

def run_recommender_demo():
    ratings = [
        (0, 0, 5.0), (0, 1, 4.0), (0, 2, 1.0),
        (1, 0, 4.5), (1, 1, 5.0), (1, 3, 2.0),
        (2, 2, 4.0), (2, 3, 5.0), (2, 0, 1.0),
        (3, 1, 4.0), (3, 2, 2.0), (3, 3, 4.5)
    ]
    mf = MatrixFactorizationSGD(n_factors=2, lr=0.05, reg=0.02, n_epochs=50).fit(ratings)
    pred_0_3 = mf.predict(0, 3)
    print(f"Recommender Demo: User 0 on Item 3 Predicted Rating = {pred_0_3:.2f}")
    return mf, pred_0_3

if __name__ == "__main__":
    run_recommender_demo()
