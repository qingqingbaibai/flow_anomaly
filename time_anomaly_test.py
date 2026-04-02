import numpy as np
import pandas as pd


# =========================
# 1️⃣ 读取数据
# =========================
edges = pd.read_csv('edges.csv')

times = sorted(edges['时间戳'].unique())
cities = sorted(edges['客户市名称'].unique())
provinces = sorted(edges['客户省名称'].unique())

num_months = len(times)
num_cities = len(cities)
num_provinces = len(provinces)

city2idx = {c:i for i,c in enumerate(cities)}
prov2idx = {p:i for i,p in enumerate(provinces)}

# city -> province
c2p = {}
for _,row in edges.iterrows():
    c = city2idx[row['客户市名称']]
    p = prov2idx[row['客户省名称']]
    c2p[c] = p

# =========================
# 2️⃣ 构建时间图数据
# =========================
data = np.zeros((num_months, num_cities, num_cities))

for t_i,t in enumerate(times):

    graph = edges[edges['时间戳']==t]

    for _,row in graph.iterrows():

        i = city2idx[row['客户市名称']]
        j = city2idx[row['开瓶市']]

        data[t_i,i,j] = row['开瓶数']

# =========================
# 3️⃣ EMA预测
# =========================
alpha = 0.6

pred = np.zeros_like(data)
pred[0] = data[0]

for t in range(1,num_months):
    pred[t] = alpha*data[t-1] + (1-alpha)*pred[t-1]

# =========================
# 4️⃣ z-score 边异常
# =========================
residual = data - pred

mean = residual.mean(axis=0)
std = residual.std(axis=0) + 1e-6

z = (residual - mean) / std


def build_history_adj(data,window=6):

    if data.shape[0] < window:
        window = data.shape[0]

    hist = data[-window:]

    A = hist.mean(axis=0)

    A = (A + A.T)/2

    np.fill_diagonal(A,0)

    D = A.sum(axis=1,keepdims=True)+1e-6

    A_norm = A/D

    return A_norm

# =========================
# 5️⃣ 城市 → 省异常聚合
# =========================
def city_to_province_anomaly(z_t,x_t,K=3,min_volume=10):

    score = np.zeros((num_cities,num_provinces))

    for i in range(num_cities):

        prov_edges = [[] for _ in range(num_provinces)]

        for j in range(num_cities):

            if x_t[i,j] < min_volume:
                continue

            p = c2p[j]

            val = z_t[i,j] * np.log(x_t[i,j]+1)

            prov_edges[p].append(val)

        for p in range(num_provinces):

            vals = sorted(prov_edges[p],reverse=True)

            if len(vals)==0:
                continue

            score[i,p] = np.mean(vals[:K])

    return score


# =========================
# 6️⃣ 节点异常分数
# =========================
def node_score_from_province(prov_score,K=2):

    n = prov_score.shape[0]

    score = np.zeros(n)

    for i in range(n):

        vals = np.sort(prov_score[i])[::-1]

        score[i] = np.mean(vals[:K])

    return score


# =========================
# 7️⃣ 图传播增强
# =========================
def graph_smooth(node_score,A,alpha=0.3,steps=3):

    x = node_score.copy()

    for _ in range(steps):
        x = (1-alpha)*x + alpha*(A@x)

    return x


# =========================
# 8️⃣ 解释函数
# =========================
def explain_city_province(i,p,z_t,x_t,min_volume=10):

    edges = []

    for j in range(num_cities):

        if c2p[j]!=p:
            continue

        if x_t[i,j] < min_volume:
            continue

        if z_t[i,j] <= 0:
            continue

        edges.append((j,z_t[i,j],x_t[i,j]))

    edges.sort(key=lambda x:-x[1])

    result = []

    for j,z_val,vol in edges[:5]:

        print(f"      {cities[i]} → {cities[j]}  z={z_val:.2f}  vol={vol:.1f}")

        result.append({
            'src':cities[i],
            'dst':cities[j],
            'z':z_val,
            'vol':vol
        })

    return result


# =========================
# 9️⃣ 主流程
# =========================
t = -1

z_t = z[t]
x_t = data[t]

# 历史邻接矩阵
A_hist = build_history_adj(data,window=6)

# 城市→省异常
prov_score = city_to_province_anomaly(z_t,x_t)

# 节点异常
node_score = node_score_from_province(prov_score)

# 图传播增强
node_score_smooth = graph_smooth(node_score,A_hist)

# Top节点
k = max(1,int(len(node_score)*0.03))

top_nodes = np.argsort(-node_score_smooth)[:k]

# %%
print("\n🚨 系统异常节点\n")

results = []
for i in top_nodes:

    print(f"📍 {cities[i]}  score={node_score_smooth[i]:.2f}")
    city_result = {
        "city": cities[i],
        "score": float(node_score_smooth[i]),
        "provinces": []
        }

    prov_vals = prov_score[i]

    prov_top = np.argsort(-prov_vals)[:3]

    for p in prov_top:

        if prov_vals[p]<=0:
            continue

        print(f"   → {provinces[p]}  anomaly={prov_vals[p]:.2f}")

        edge_results = explain_city_province(i,p,z_t,x_t)
        province_result = {
            "province": provinces[p],
            "score": float(prov_vals[p]),
            "edges": []
        }
        province_result["edges"] = edge_results
        province_result['vol'] = sum([e['vol'] for e in edge_results])
        city_result["provinces"].append(province_result)
    
    results.append(city_result)

    print("-"*50)

import json

with open("anomaly_result.json","w",encoding="utf8") as f:
    json.dump(results,f,ensure_ascii=False,indent=2)


