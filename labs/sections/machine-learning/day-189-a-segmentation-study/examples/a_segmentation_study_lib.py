import numpy as np

class CustomerSegmentationPipeline:
    def __init__(self, n_clusters=4, variance_threshold=0.90, random_state=42):
        self.n_clusters = n_clusters
        self.variance_threshold = variance_threshold
        self.random_state = random_state
        self.mean_ = None
        self.std_ = None
        self.pca_components_ = None
        self.centroids_ = None
        self.labels_ = None

    def _log_standardize(self, X_raw):
        X_log = np.log1p(np.maximum(X_raw, 0))
        if self.mean_ is None:
            self.mean_ = np.mean(X_log, axis=0)
            self.std_ = np.std(X_log, axis=0) + 1e-12
        return (X_log - self.mean_) / self.std_

    def _fit_pca(self, X_scaled):
        U, S, Vt = np.linalg.svd(X_scaled, full_matrices=False)
        evr = (S ** 2) / np.sum(S ** 2)
        cum_evr = np.cumsum(evr)
        k = int(np.searchsorted(cum_evr, self.variance_threshold)) + 1
        k = max(2, min(k, X_scaled.shape[1]))
        self.pca_components_ = Vt[:k]
        return np.dot(X_scaled, self.pca_components_.T)

    def _kmeans_pp(self, Z, k):
        rng = np.random.default_rng(self.random_state)
        n_samples = len(Z)
        centroids = [Z[rng.choice(n_samples)]]

        for _ in range(1, k):
            dists = np.min([np.sum((Z - c)**2, axis=1) for c in centroids], axis=0)
            probs = dists / (np.sum(dists) + 1e-12)
            centroids.append(Z[rng.choice(n_samples, p=probs)])

        centroids = np.array(centroids)
        for _ in range(100):
            dists = np.array([np.sum((Z - c)**2, axis=1) for c in centroids])
            labels = np.argmin(dists, axis=0)
            new_centroids = np.array([Z[labels == j].mean(axis=0) if np.sum(labels == j) > 0 else centroids[j] for j in range(k)])
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids

        return centroids, labels

    def fit(self, X_raw):
        X_scaled = self._log_standardize(X_raw)
        Z = self._fit_pca(X_scaled)
        self.centroids_, self.labels_ = self._kmeans_pp(Z, self.n_clusters)
        return self

    def compute_persona_profiles(self, X_raw):
        profiles = {}
        for k in range(self.n_clusters):
            mask = (self.labels_ == k)
            if np.sum(mask) > 0:
                profiles[f"Cluster_{k}"] = {
                    "count": int(np.sum(mask)),
                    "mean_recency": float(np.mean(X_raw[mask, 0])),
                    "mean_frequency": float(np.mean(X_raw[mask, 1])),
                    "mean_monetary": float(np.mean(X_raw[mask, 2]))
                }
        return profiles

def run_segmentation_demo():
    np.random.seed(42)
    # Generate 4 distinct customer personas
    # [Recency (days), Frequency (orders), Monetary ($)]
    c1 = np.random.normal(loc=[5.0, 50.0, 5000.0], scale=[2.0, 5.0, 500.0], size=(100, 3))   # VIP
    c2 = np.random.normal(loc=[30.0, 15.0, 1200.0], scale=[5.0, 3.0, 200.0], size=(100, 3))  # Steady
    c3 = np.random.normal(loc=[10.0, 2.0, 150.0], scale=[3.0, 1.0, 30.0], size=(100, 3))     # New
    c4 = np.random.normal(loc=[250.0, 8.0, 600.0], scale=[20.0, 2.0, 100.0], size=(100, 3))  # Churn
    X = np.maximum(np.vstack([c1, c2, c3, c4]), 0)

    pipe = CustomerSegmentationPipeline(n_clusters=4).fit(X)
    profiles = pipe.compute_persona_profiles(X)
    print(f"Segmentation Demo: Processed {len(X)} customers into {len(profiles)} personas.")
    return pipe, profiles

if __name__ == "__main__":
    run_segmentation_demo()
