import pandas as pd
import numpy as np
from sklearn.metrics import (precision_recall_curve, average_precision_score, precision_score, recall_score, confusion_matrix)

def evaluate(y_true, y_prob):
    prec, rec, thr = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)

    rows = []
    for t in [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]:
        pred = (y_prob >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
        rows.append({
            "threshold": t,
            "precision": tp / (tp + fp) if tp + fp else np.nan,
            "recall": tp / (tp + fn),
            "fpr": fp / (fp + tn),
            "flagged": pred.sum()
        })
    return ap, pd.DataFrame(rows)

