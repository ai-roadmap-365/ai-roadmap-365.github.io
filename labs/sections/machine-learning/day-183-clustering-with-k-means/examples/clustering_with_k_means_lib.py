import numpy as np

class KMeansFromScratch:
    def __init__(self, n_clusters=3, max_iter=300, tol=1e-4, init='k-means++', random_state=42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.random_state = random_state
        self.cluster_centers_ = None
        self.inertia_ = None

    def _init_centroids(self, X, rng):
        n_samples, n_features = X.shape
        if self.init == 'random':
            indices = rng.choice(n_samples, size=self.n_clusters, replace=False)
            return X[indices].copy()

        centers = np.empty((self.n_clusters, n_features))
        first_idx = rng.integers(0, n_samples)
        centers[0] = X[first_idx]

        for k in range(1, self.n_clusters):
            # (n, 1, d) - (1, k, d) -> (n, k, d): every point against every
            # chosen centre. Putting the newaxis on the wrong side of centers
            # collapses this to a single distance and probs comes out length 1.
            diff = X[:, np.newaxis, :] - centers[np.newaxis, :k, :]
            dists = np.min(np.linalg.norm(diff, axis=2) ** 2, axis=1)
            probs = dists / np.sum(dists)
            next_idx = rng.choice(n_samples, p=probs)
            centers[k] = X[next_idx]

        return centers

    def fit(self, X):
        rng = np.random.default_rng(self.random_state)
        self.cluster_centers_ = self._init_centroids(X, rng)

        for iteration in range(self.max_iter):
            dists = np.linalg.norm(X[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :], axis=2)
            labels = np.argmin(dists, axis=1)

            new_centers = np.zeros_like(self.cluster_centers_)
            for k in range(self.n_clusters):
                mask = labels == k
                if np.sum(mask) > 0:
                    new_centers[k] = np.mean(X[mask], axis=0)
                else:
                    new_centers[k] = X[rng.integers(0, len(X))]

            shift = np.linalg.norm(self.cluster_centers_ - new_centers)
            self.cluster_centers_ = new_centers
            if shift < self.tol:
                break

        dists = np.linalg.norm(X[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :], axis=2)
        labels = np.argmin(dists, axis=1)
        min_dists = np.min(dists, axis=1)
        self.inertia_ = float(np.sum(min_dists**2))
        return self

    def predict(self, X):
        dists = np.linalg.norm(X[:, np.newaxis, :] - self.cluster_centers_[np.newaxis, :, :], axis=2)
        return np.argmin(dists, axis=1)

def run_kmeans_demo():
    np.random.seed(42)
    c1 = np.random.normal(loc=[-4.0, -4.0], scale=0.8, size=(100, 2))
    c2 = np.random.normal(loc=[4.0, 4.0], scale=0.8, size=(100, 2))
    c3 = np.random.normal(loc=[0.0, 5.0], scale=0.8, size=(100, 2))
    X = np.vstack([c1, c2, c3])

    kmeans = KMeansFromScratch(n_clusters=3, random_state=42).fit(X)
    labels = kmeans.predict(X)
    print(f"K-Means converged with Inertia: {kmeans.inertia_:.2f}")
    return kmeans, labels

if __name__ == "__main__":
    run_kmeans_demo()
