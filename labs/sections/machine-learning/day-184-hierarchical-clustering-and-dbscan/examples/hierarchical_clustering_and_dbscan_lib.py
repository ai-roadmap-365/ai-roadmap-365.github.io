import numpy as np

class DBSCANFromScratch:
    def __init__(self, eps=0.5, min_samples=5):
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None

    def fit(self, X):
        n_samples = len(X)
        self.labels_ = np.full(n_samples, -1)
        cluster_id = 0

        dists = np.linalg.norm(X[:, np.newaxis, :] - X[np.newaxis, :, :], axis=2)

        for i in range(n_samples):
            if self.labels_[i] != -1:
                continue

            neighbors = np.where(dists[i] <= self.eps)[0]
            if len(neighbors) < self.min_samples:
                continue

            self.labels_[i] = cluster_id
            queue = list(neighbors[neighbors != i])

            while queue:
                current_point = queue.pop(0)
                if self.labels_[current_point] == -1:
                    self.labels_[current_point] = cluster_id

                curr_neighbors = np.where(dists[current_point] <= self.eps)[0]
                if len(curr_neighbors) >= self.min_samples:
                    for n in curr_neighbors:
                        if self.labels_[n] == -1:
                            self.labels_[n] = cluster_id
                            queue.append(n)

            cluster_id += 1

        return self

def run_dbscan_demo():
    np.random.seed(42)
    c1 = np.random.normal(loc=[-3.0, 0.0], scale=0.3, size=(50, 2))
    c2 = np.random.normal(loc=[3.0, 0.0], scale=0.3, size=(50, 2))
    noise = np.array([[10.0, 10.0], [-10.0, 10.0], [0.0, -10.0]])
    X = np.vstack([c1, c2, noise])

    db = DBSCANFromScratch(eps=0.8, min_samples=5).fit(X)
    n_clusters = len(set(db.labels_) - {-1})
    n_noise = int(np.sum(db.labels_ == -1))
    print(f"DBSCAN Demo: Discovered {n_clusters} clusters with {n_noise} noise points.")
    return db, n_clusters, n_noise

if __name__ == "__main__":
    run_dbscan_demo()
