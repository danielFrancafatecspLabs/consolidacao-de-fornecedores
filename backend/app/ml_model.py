import numpy as np
import pandas as pd

def analyze_best_supplier(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Filter out invalid rows
    df = df.dropna(subset=["hh", "hora", "total"])

    # Find the best supplier
    best_supplier = df.loc[df["total"].idxmin()]

    return {
        "fornecedor": best_supplier["fornecedor"],
        "total": best_supplier["total"],
        "hh": best_supplier["hh"],
        "hora": best_supplier["hora"],
    }