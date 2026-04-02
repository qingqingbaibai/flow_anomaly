# %%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import json

if os.path.exists('edges.csv'):
    exit()

# 开瓶信息
df_sheet1 = pd.read_excel('./data.xlsx', sheet_name=0)  # sheet_name=0 表示第一个sheet
df_sheet2 = pd.read_excel('./data.xlsx', sheet_name=1, header=None, names=df_sheet1.columns)  # sheet_name=1 表示第二个sheet
df_sheet3 = pd.read_excel('./data.xlsx', sheet_name=2, header=None, names=df_sheet1.columns)
data = pd.concat([df_sheet1, df_sheet2, df_sheet3], axis=0, ignore_index=True)

# 保留客户在的城市
nodes = data['客户市名称'].dropna().unique().tolist()
data = data[data['开瓶市'].isin(nodes)]


def edge_agg(group):
    _, province1, city1, province2, city2 = group.name
    result = {}
    # 出边基础指标
    result['是否跨市'] = 0 if city1 == city2 else 1
    result['是否跨省'] = 0 if province1 == province2 else 1
    
    # result['批次量'] = group['批次'].count()
    result['开瓶数'] = group['开瓶数'].sum()
    # result['开瓶距离最后入库最大天数'] = group['开瓶距离最后入库最大天数'].max()
    # result['开瓶距离最后入库最小天数'] = group['开瓶距离最后入库最小天数'].min()
    # result['平均开箱次序'] = (group['平均开箱次序'] * group['开瓶数']).sum() / group['开瓶数'].sum()

    # 出表高阶指标
    # 开瓶集中度
    # p = group['开瓶数'] / group['开瓶数'].sum()
    # result['批次集中度'] = 1 - (-p * np.log(p)).sum()/np.log(len(group)) if len(group) > 1 else 1
    # 开瓶速度
    # result['平均开瓶速度'] = (group['开瓶距离最后入库平均天数'] * group['开瓶数']).sum() / group['开瓶数'].sum()

    return pd.Series(result)

def node_agg(group):
    time, city = group.name
    result = {}
    # 节点基础指标
    result['开瓶数'] = group['开瓶数'].sum()
    
    ########################################## 
    group_in = group[group['是否流出']==0]
    # 本地开瓶指标
    result['批次量（本地）'] = group_in['批次量'].iloc[0] if len(group_in) > 0 else 0
    result['开瓶数（本地）'] = group_in['开瓶数'].iloc[0] if len(group_in) > 0 else 0
    result['批次集中度（本地）'] = group_in['批次集中度'].iloc[0] if len(group_in) > 0 else 0
    # result['平均开瓶速度（本地）'] = group_in['平均开瓶速度'].iloc[0] if len(group_in) > 0 else 0
    

    ##########################################
    group_out = group[group['是否流出']==1]
    # 异地开瓶指标
    result['流出城市数'] = group_out['开瓶市'].nunique() if len(group_out) > 0 else 0
    result['异地开瓶数'] = group_out['开瓶数'].sum() if len(group_out) > 0 else 0
    # result['开瓶距离最后入库最大天数'] = group_out['开瓶距离最后入库最大天数'].max() if len(group_out) > 0 else 0
    # result['开瓶距离最后入库最小天数'] = group_out['开瓶距离最后入库最小天数'].min() if len(group_out) > 0 else 0

    # 节点高阶指标
    p = group_out['开瓶数']/ group_out['开瓶数'].sum()
    result['流出城市集中度'] = 1 - (-p * np.log(p)).sum()/np.log(len(group_out)) if len(group_out) > 1 else 1
    # 开瓶速度
    # result['流出平均开瓶速度'] = (group_out['平均开瓶速度'] * group_out['开瓶数']).sum() / group_out['开瓶数'].sum() if len(group_out) > 0 else 0
    # 异地率
    result['异地率'] = result['异地开瓶数'] / result['开瓶数']
    
    return pd.Series(result)

# 按照时间戳、客户市名称、开瓶市进行分组，计算出边指标
edges = data.groupby(['时间戳', '客户省名称', '客户市名称', '开瓶省', '开瓶市']).apply(edge_agg)
edges = edges.reset_index()
edges.to_csv('edges.csv', index=False)

# # 按照时间戳、客户市名称进行分组，计算出节点指标
# if os.path.exists('nodes.csv'):
#     nodes = pd.read_csv('nodes.csv')
# else:
#     nodes = edges.groupby(['时间戳', '客户市名称']).apply(node_agg)
#     nodes = nodes.reset_index()
#     nodes.to_csv('nodes.csv', index=False)



