import numpy as np

def compute_fairness_metrics(y_true, y_pred, sensitive_attr):
    """
    Compute core algorithmic fairness metrics across binary sensitive attribute groups (0 vs 1).
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    sens = np.asarray(sensitive_attr, dtype=int)
    
    # Subgroup masks
    mask_0 = (sens == 0)
    mask_1 = (sens == 1)
    
    # Selection Rates (Demographic Parity)
    sr_0 = np.mean(y_pred[mask_0]) if np.sum(mask_0) > 0 else 0.0
    sr_1 = np.mean(y_pred[mask_1]) if np.sum(mask_1) > 0 else 0.0
    
    dp_diff = abs(sr_0 - sr_1)
    disparate_impact_ratio = min(sr_0, sr_1) / max(max(sr_0, sr_1), 1e-9)
    
    # Group Confusion Matrices
    def get_group_rates(mask):
        tp = np.sum((y_true[mask] == 1) & (y_pred[mask] == 1))
        tn = np.sum((y_true[mask] == 0) & (y_pred[mask] == 0))
        fp = np.sum((y_true[mask] == 0) & (y_pred[mask] == 1))
        fn = np.sum((y_true[mask] == 1) & (y_pred[mask] == 0))
        
        tpr = tp / max(tp + fn, 1e-9)
        fpr = fp / max(tn + fp, 1e-9)
        prec = tp / max(tp + fp, 1e-9)
        return float(tpr), float(fpr), float(prec)
        
    tpr_0, fpr_0, prec_0 = get_group_rates(mask_0)
    tpr_1, fpr_1, prec_1 = get_group_rates(mask_1)
    
    # Equal Opportunity (TPR difference)
    eq_opp_diff = abs(tpr_0 - tpr_1)
    
    # Equalized Odds (Max of TPR and FPR differences)
    eq_odds_diff = max(abs(tpr_0 - tpr_1), abs(fpr_0 - fpr_1))
    
    # Predictive Parity (Precision difference)
    pred_parity_diff = abs(prec_0 - prec_1)
    
    return {
        "group_0": {"selection_rate": float(sr_0), "tpr": tpr_0, "fpr": fpr_0, "precision": prec_0},
        "group_1": {"selection_rate": float(sr_1), "tpr": tpr_1, "fpr": fpr_1, "precision": prec_1},
        "demographic_parity_difference": float(dp_diff),
        "disparate_impact_ratio": float(disparate_impact_ratio),
        "equal_opportunity_difference": float(eq_opp_diff),
        "equalized_odds_difference": float(eq_odds_diff),
        "predictive_parity_difference": float(pred_parity_diff),
    }

def compute_reweighing_weights(y_true, sensitive_attr):
    """
    Calculate sample weights for pre-processing debiasing (Kamiran & Calders 2012).
    W(A=a, Y=y) = P(A=a) * P(Y=y) / P(A=a, Y=y)
    """
    y_true = np.asarray(y_true, dtype=int)
    sens = np.asarray(sensitive_attr, dtype=int)
    n = len(y_true)
    
    weights = np.ones(n, dtype=float)
    
    for a in [0, 1]:
        for y in [0, 1]:
            p_a = np.mean(sens == a)
            p_y = np.mean(y_true == y)
            p_ay = np.mean((sens == a) & (y_true == y))
            
            w = (p_a * p_y) / max(p_ay, 1e-9)
            mask = (sens == a) & (y_true == y)
            weights[mask] = w
            
    return weights

def calibrate_group_thresholds_for_equal_opportunity(y_true, y_prob, sensitive_attr, target_tpr=0.80):
    """
    Post-processing calibration: Find separate thresholds T_0 and T_1 to equalize True Positive Rate.
    """
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    sens = np.asarray(sensitive_attr, dtype=int)
    
    def find_threshold_for_target_tpr(mask):
        y_t = y_true[mask]
        y_p = y_prob[mask]
        
        pos_probs = y_p[y_t == 1]
        if len(pos_probs) == 0:
            return 0.5
        # Threshold at (1 - target_tpr) percentile of positive probabilities
        thresh = float(np.percentile(pos_probs, (1.0 - target_tpr) * 100.0))
        return thresh
        
    t_0 = find_threshold_for_target_tpr(sens == 0)
    t_1 = find_threshold_for_target_tpr(sens == 1)
    
    return {"threshold_group_0": t_0, "threshold_group_1": t_1}
