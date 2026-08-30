import json
import re
from typing import Dict, Any

class EvalMetricEngine:
    @staticmethod
    def exact_match(prediction: str, ground_truth: str) -> float:
        norm_pred = prediction.strip().lower()
        norm_gt = ground_truth.strip().lower()
        return 1.0 if norm_pred == norm_gt else 0.0
        
    @staticmethod
    def json_field_f1(predicted_json_str: str, ground_truth_dict: Dict[str, Any]) -> Dict[str, float]:
        try:
            pred_dict = json.loads(predicted_json_str)
        except Exception:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "valid_json": 0.0}
            
        if not isinstance(pred_dict, dict):
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "valid_json": 0.0}
            
        correct_fields = 0
        total_pred_fields = len(pred_dict)
        total_gt_fields = len(ground_truth_dict)
        
        for k, v in pred_dict.items():
            if k in ground_truth_dict and str(ground_truth_dict[k]).strip().lower() == str(v).strip().lower():
                correct_fields += 1
                
        precision = correct_fields / total_pred_fields if total_pred_fields > 0 else 0.0
        recall = correct_fields / total_gt_fields if total_gt_fields > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "valid_json": 1.0,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        }
        
    @staticmethod
    def token_overlap_f1(prediction: str, ground_truth: str) -> float:
        pred_tokens = set(re.findall(r'\w+', prediction.lower()))
        gt_tokens = set(re.findall(r'\w+', ground_truth.lower()))
        
        if not pred_tokens or not gt_tokens:
            return 0.0
            
        common = pred_tokens.intersection(gt_tokens)
        if not common:
            return 0.0
            
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(gt_tokens)
        return round((2 * precision * recall) / (precision + recall), 4)

if __name__ == "__main__":
    engine = EvalMetricEngine()
    print("Exact Match:", engine.exact_match("Paris", "paris"))
