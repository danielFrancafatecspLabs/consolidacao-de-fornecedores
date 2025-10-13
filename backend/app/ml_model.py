import numpy as np
import pandas as pd

def analyze_best_supplier(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Filter out invalid rows
    df = df.dropna(subset=["hh", "hora", "total"])

    # Predict cost-benefit score
    df["score"] = df["total"] / (df["hh"] + df["hora"])

    # Find the best supplier
    best_supplier = df.loc[df["score"].idxmin()]

    return {
        "fornecedor": best_supplier["fornecedor"],
        "score": best_supplier["score"],
        "total": best_supplier["total"],
        "hh": best_supplier["hh"],
        "hora": best_supplier["hora"],
    }