import pandas as pd

# Enhanced fusion sonuçlarını oku
df = pd.read_csv("../results/enhanced_fusion_table.csv")

# Denenecek eşikler
display_thresholds = [0.65, 0.70, 0.75, 0.80]
suppress_thresholds = [0.30, 0.35, 0.40, 0.45]

results = []

for d_th in display_thresholds:
    for s_th in suppress_thresholds:
        if s_th >= d_th:
            continue

        decisions = []
        for r in df["final_reliability"]:
            if r > d_th:
                decisions.append("DISPLAY")
            elif r < s_th:
                decisions.append("SUPPRESS")
            else:
                decisions.append("WARNING")

        temp = pd.Series(decisions).value_counts()

        display_count = temp.get("DISPLAY", 0)
        warning_count = temp.get("WARNING", 0)
        suppress_count = temp.get("SUPPRESS", 0)

        results.append({
            "display_threshold": d_th,
            "suppress_threshold": s_th,
            "DISPLAY": display_count,
            "WARNING": warning_count,
            "SUPPRESS": suppress_count
        })

result_df = pd.DataFrame(results)

print(result_df.sort_values(["display_threshold", "suppress_threshold"]))

result_df.to_csv("../results/threshold_sweep_results.csv", index=False)

print("\nKaydedildi: ../results/threshold_sweep_results.csv")
