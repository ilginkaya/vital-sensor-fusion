import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# enhanced fusion sonuçlarını oku
df = pd.read_csv("../results/enhanced_fusion_table.csv")

motion = df["motion_score"]
reliability = df["final_reliability"]

# korelasyon
corr = np.corrcoef(motion, reliability)[0,1]

print("Correlation (motion vs reliability):", corr)

plt.figure(figsize=(6,6))
plt.scatter(motion, reliability, alpha=0.5)

plt.xlabel("Motion Score")
plt.ylabel("Final Reliability")
plt.title("Motion vs Reliability Relationship")

plt.grid(True)

plt.savefig("../results/motion_vs_reliability.png", dpi=300)

plt.show()
