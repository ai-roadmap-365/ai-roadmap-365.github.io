import numpy as np

class PCAFromScratch:
    def __init__(self, n_components=2, whiten=False):
        self.n_components = n_components
        self.whiten = whiten
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None

    def fit(self, X):
        n_samples, n_features = X.shape
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)

        explained_variance = (S ** 2) / (n_samples - 1)
        total_variance = np.sum(explained_variance)
        explained_variance_ratio = explained_variance / total_variance

        self.components_ = Vt[:self.n_components]
        self.explained_variance_ = explained_variance[:self.n_components]
        self.explained_variance_ratio_ = explained_variance_ratio[:self.n_components]
        return self

    def transform(self, X):
        X_centered = X - self.mean_
        Z = np.dot(X_centered, self.components_.T)
        if self.whiten:
            scale = np.sqrt(self.explained_variance_) + 1e-12
            Z = Z / scale
        return Z

    def inverse_transform(self, Z):
        if self.whiten:
            scale = np.sqrt(self.explained_variance_) + 1e-12
            Z = Z * scale
        return np.dot(Z, self.components_) + self.mean_

def run_pca_demo():
    np.random.seed(42)
    X = np.random.normal(0, 1, (200, 5))
    X[:, 1] = X[:, 0] * 2.0 + np.random.normal(0, 0.2, 200)

    pca = PCAFromScratch(n_components=2).fit(X)
    Z = pca.transform(X)
    X_rec = pca.inverse_transform(Z)
    mse = float(np.mean((X - X_rec) ** 2))
    print(f"PCA Demo: Input Shape {X.shape} -> Reduced {Z.shape}, Reconstruction MSE = {mse:.4f}")
    return pca, Z, mse

if __name__ == "__main__":
    run_pca_demo()
