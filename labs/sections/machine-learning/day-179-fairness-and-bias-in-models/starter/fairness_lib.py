import numpy as np

def compute_fairness_metrics(y_true, y_pred, sensitive_attr):
    # TODO: Implement Demographic Parity, Equal Opportunity, Equalized Odds, and Predictive Parity
    pass

def compute_reweighing_weights(y_true, sensitive_attr):
    # TODO: Implement Kamiran & Calders sample reweighing
    pass

def calibrate_group_thresholds_for_equal_opportunity(y_true, y_prob, sensitive_attr, target_tpr=0.80):
    # TODO: Find group-specific thresholds achieving equal True Positive Rates
    pass
