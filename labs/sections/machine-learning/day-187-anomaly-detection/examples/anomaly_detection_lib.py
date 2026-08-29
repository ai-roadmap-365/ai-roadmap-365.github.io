import numpy as np

def c_factor(n):
    if n <= 1:
        return 0.0
    if n == 2:
        return 1.0
    # Euler-Mascheroni constant = 0.5772156649
    return 2.0 * (np.log(n - 1) + 0.5772156649) - (2.0 * (n - 1) / n)

class IsolationTree:
    def __init__(self, current_depth=0, max_depth=10):
        self.current_depth = current_depth
        self.max_depth = max_depth
        self.split_feature = None
        self.split_value = None
        self.left = None
        self.right = None
        self.size = 0
        self.is_leaf = False

    def fit(self, X):
        self.size = len(X)
        if self.current_depth >= self.max_depth or self.size <= 1:
            self.is_leaf = True
            return self

        n_features = X.shape[1]
        self.split_feature = np.random.randint(0, n_features)
        feat_vals = X[:, self.split_feature]
        min_val, max_val = np.min(feat_vals), np.max(feat_vals)

        if np.isclose(min_val, max_val):
            self.is_leaf = True
            return self

        self.split_value = np.random.uniform(min_val, max_val)
        left_mask = feat_vals < self.split_value
        right_mask = ~left_mask

        self.left = IsolationTree(self.current_depth + 1, self.max_depth).fit(X[left_mask])
        self.right = IsolationTree(self.current_depth + 1, self.max_depth).fit(X[right_mask])
        return self

    def path_length(self, x):
        if self.is_leaf:
            return self.current_depth + c_factor(self.size)
        if x[self.split_feature] < self.split_value:
            return self.left.path_length(x)
        else:
            return self.right.path_length(x)

class IsolationForestFromScratch:
    def __init__(self, n_estimators=50, max_samples=128, contamination=0.05, random_state=42):
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.random_state = random_state
        self.trees = []
        self.threshold_ = None

    def fit(self, X):
        rng = np.random.default_rng(self.random_state)
        n_samples = len(X)
        subsample_size = min(self.max_samples, n_samples)
        max_depth = int(np.ceil(np.log2(max(subsample_size, 2))))

        self.trees = []
        for _ in range(self.n_estimators):
            idx = rng.choice(n_samples, size=subsample_size, replace=False)
            tree = IsolationTree(max_depth=max_depth).fit(X[idx])
            self.trees.append(tree)

        scores = self.decision_function(X)
        self.threshold_ = np.percentile(scores, 100.0 * (1.0 - self.contamination))
        return self

    def decision_function(self, X):
        n_samples = len(X)
        paths = np.zeros((n_samples, self.n_estimators))
        for t_idx, tree in enumerate(self.trees):
            for i in range(n_samples):
                paths[i, t_idx] = tree.path_length(X[i])

        avg_paths = np.mean(paths, axis=1)
        scores = 2.0 ** (-avg_paths / c_factor(self.max_samples))
        return scores

    def predict(self, X):
        scores = self.decision_function(X)
        return np.where(scores >= self.threshold_, -1, 1)

def run_anomaly_demo():
    np.random.seed(42)
    inliers = np.random.normal(0, 1, (300, 2))
    outliers = np.random.uniform(low=-8, high=8, size=(15, 2))
    X = np.vstack([inliers, outliers])

    clf = IsolationForestFromScratch(n_estimators=50, max_samples=128, contamination=0.05).fit(X)
    scores = clf.decision_function(X)
    inlier_mean = float(np.mean(scores[:300]))
    outlier_mean = float(np.mean(scores[300:]))

    print(f"Anomaly Demo: Inlier Mean Score = {inlier_mean:.4f}, Outlier Mean Score = {outlier_mean:.4f}")
    return clf, inlier_mean, outlier_mean

if __name__ == "__main__":
    run_anomaly_demo()
