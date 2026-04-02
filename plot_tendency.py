import pandas as pd
import matplotlib.pyplot as plt
import math, os
import json
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# =========================
# 1️⃣ 读取数据
# =========================
edges = pd.read_csv("./edges.csv")

with open("./anomaly_result.json", "r", encoding="utf-8") as f:
    anomaly_list = json.load(f)

edges["时间戳"] = pd.to_datetime(edges["时间戳"])
edges["month"] = edges["时间戳"].dt.to_period("M")

# 创建图片目录
os.makedirs("./report/plots", exist_ok=True)

# 全部月份，用于补齐
all_months = pd.period_range(edges["month"].min(), edges["month"].max(), freq="M")

# =========================
# 2️⃣ 获取时间序列
# =========================
def get_flow_series(src_city, dst_province):
    """获取城市到省份的月度流入序列"""
    df = edges[(edges["客户市名称"] == src_city) & (edges["开瓶省"] == dst_province)]
    ts = df.groupby("month")["开瓶数"].sum()
    ts = ts.reindex(all_months, fill_value=0)
    return ts


# =========================
# 3️⃣ 绘图
# =========================
for item in anomaly_list:
    src_city = item["city"]
    provinces = item["provinces"]

    # 每个省一个子图
    n_subplots = len(provinces)
    fig, axes = plt.subplots(n_subplots, 1, figsize=(12, 4*n_subplots), sharex=True)

    if n_subplots == 1:
        axes = [axes]

    for i, prov_data in enumerate(provinces):
        prov = prov_data["province"]

        ts = get_flow_series(src_city, prov)

        ax = axes[i]
        ax.plot(ts.index.to_timestamp(), ts.values, marker="o", color="tab:blue")
        ax.set_title(f"{src_city} → {prov} 月度流入趋势")
        ax.set_ylabel("开瓶数")
        ax.grid(True)
    
    axes[-1].set_xlabel("月份")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"./report/plots/{src_city}_province_trends.png", dpi=300)
    plt.close()

print("✅ 所有城市到各省份趋势图已生成，保存在 report/plots/ 文件夹")


