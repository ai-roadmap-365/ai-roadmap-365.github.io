import numpy as np

class TSNEFromScratch:
    def __init__(self, n_components=2, perplexity=30.0, n_iter=300, lr=100.0, random_state=42):
        self.n_components = n_components
        self.perplexity = perplexity
        self.n_iter = n_iter
        self.lr = lr
        self.random_state = random_state
        self.embedding_ = None

    def _compute_affinities(self, X):
        n_samples = len(X)
        dists = np.linalg.norm(X[:, np.newaxis, :] - X[np.newaxis, :, :], axis=2)**2
        P = np.zeros((n_samples, n_samples))

        sigmas = np.median(dists, axis=1) / np.log(self.perplexity)
        for i in range(n_samples):
            num = np.exp(-dists[i] / (2.0 * sigmas[i] + 1e-12))
            num[i] = 0.0
            P[i] = num / (np.sum(num) + 1e-12)

        P = (P + P.T) / (2.0 * n_samples)
        P = np.maximum(P, 1e-12)
        return P

    def fit_transform(self, X):
        rng = np.random.default_rng(self.random_state)
        n_samples = len(X)
        P = self._compute_affinities(X)

        P_exagg = P * 4.0
        Y = rng.normal(0, 1e-4, (n_samples, self.n_components))
        velocity = np.zeros_like(Y)
        momentum = 0.5

        for step in range(self.n_iter):
            if step == 50:
                momentum = 0.8
                P_exagg = P

            dist_Y = np.linalg.norm(Y[:, np.newaxis, :] - Y[np.newaxis, :, :], axis=2)**2
            inv_dist = 1.0 / (1.0 + dist_Y)
            np.fill_diagonal(inv_dist, 0.0)
            Q = inv_dist / (np.sum(inv_dist) + 1e-12)
            Q = np.maximum(Q, 1e-12)

            PQ_diff = (P_exagg - Q) * inv_dist
            grad = np.zeros_like(Y)
            for i in range(n_samples):
                grad[i] = 4.0 * np.sum((Y[i] - Y) * PQ_diff[i, :, np.newaxis], axis=0)

            velocity = momentum * velocity - self.lr * grad
            Y += velocity

        self.embedding_ = Y
        return Y

def run_tsne_demo():
    np.random.seed(42)
    # loc must match the number of FEATURES, not the number of components.
    # A 2-element loc against size=(40, 4) cannot broadcast and raises.
    c1 = np.random.normal(loc=[-5.0, -5.0, -5.0, -5.0], scale=0.5, size=(40, 4))
    c2 = np.random.normal(loc=[5.0, 5.0, 5.0, 5.0], scale=0.5, size=(40, 4))
    X = np.vstack([c1, c2])

    tsne = TSNEFromScratch(n_components=2, perplexity=20.0, n_iter=100, lr=50.0).fit_transform(X)
    print(f"t-SNE Demo: Transformed {X.shape} to Embedding {tsne.shape}")
    return tsne

if __name__ == "__main__":
    run_tsne_demo()
