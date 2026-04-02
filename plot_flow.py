import pandas as pd
import json, os

# 创建图片目录
os.makedirs("./report", exist_ok=True)

# 1. 城市经纬度
with open('./region.json', 'r', encoding='utf-8') as f:
    region = json.load(f)
city_locs = {}
for province in region['districts']:
    for city in province['districts']:
        if city['name'] == '重庆城区' or city['name'] == '天津城区' or city['name'] == '上海城区' or city['name'] == '北京城区':
            city_locs[city['name'][:2]+'市'] = [city['center']['longitude'], city['center']['latitude']]
        else:
            city_locs[city['name']] = [city['center']['longitude'], city['center']['latitude']]

pro_locs ={}
for province in region['districts']:
    pro_locs[province['name']] = [province['center']['longitude'], province['center']['latitude']]

with open("./anomaly_result.json", "r", encoding="utf-8") as f:
    anomaly_list = json.load(f)


anomaly_node = []
for c in anomaly_list:
    anomaly_node.append({'city': c['city']
                        , 'lat': city_locs[c['city']][1]
                        , 'lon': city_locs[c['city']][0]
                        , 'score': c['score']})
    for p in c['provinces']:
        anomaly_node.append({'city': p['province']
                            , 'lat': pro_locs[p['province']][1]
                            , 'lon': pro_locs[p['province']][0]
                            , 'score': 0})
anomaly_node = pd.DataFrame(anomaly_node).drop_duplicates()


anomaly_edge = []
for c in anomaly_list:
    for p in c['provinces']:
        anomaly_edge.append({'h': c['city']
                            , 'w': p['province']
                            , 'vol': p['vol']})
anomaly_edge = pd.DataFrame(anomaly_edge)


from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType
import pandas as pd

# -------------------------
# 示例数据
# -------------------------
# 节点数据
# anomaly_node = pd.DataFrame({
#     "city": ["北京","上海","广州","深圳","杭州","成都","泰州","重庆"],
#     "lat": [39.9042,31.2304,23.1291,22.5431,30.2741,30.5728,32.4555,29.5630],
#     "lon": [116.4074,121.4737,113.2644,114.0579,120.1551,104.0665,119.9230,106.5516],
#     "score": [5,8,3,6,2,7,10,10]
# })

# 边数据
# anomaly_edge = pd.DataFrame({
#     "h": ["北京","上海","广州","深圳","泰州","重庆"],
#     "w": ["上海","广州","深圳","成都","江苏","四川"],
#     "vol": [10, 30, 50, 20, 60, 40]
# })

# -------------------------
# 创建地图
# -------------------------
geo = Geo(
    init_opts=opts.InitOpts(width="1200px", height="800px", bg_color="white")
)
geo.add_schema(maptype="china")

# -------------------------
# 添加节点坐标
# -------------------------
for _, row in anomaly_node.iterrows():
    geo.add_coordinate(row["city"], row["lon"], row["lat"])

# -------------------------
# h 节点显示
# -------------------------
h_nodes = anomaly_edge['h'].unique()
h_node_data = anomaly_node[anomaly_node['city'].isin(h_nodes)]

geo.add(
    "h节点",
    [(row["city"], row["score"]) for _, row in h_node_data.iterrows()],
    type_=ChartType.EFFECT_SCATTER,
    symbol_size=[row["score"] * 4 for _, row in h_node_data.iterrows()],
    label_opts=opts.LabelOpts(is_show=True, formatter="{b}"),
    itemstyle_opts=opts.ItemStyleOpts(color="blue"),
    # level=2
)

# -------------------------
# 边，颜色渐变表示 vol
# -------------------------
vol_min = anomaly_edge['vol'].min()
vol_max = anomaly_edge['vol'].max()

def get_color_by_vol(vol):
    intensity = int(100 + 155 * (vol - vol_min) / (vol_max - vol_min))
    return f"rgb({intensity},0,0)"

for _, row in anomaly_edge.iterrows():
    color = get_color_by_vol(row['vol'])
    geo.add(
        f"{row['h']}→{row['w']}",
        [[row['h'], row['w']]],
        type_=ChartType.LINES,
        linestyle_opts=opts.LineStyleOpts(width=2, color=color, opacity=0.8, curve=0.2),
        effect_opts=opts.EffectOpts(symbol=SymbolType.ARROW, symbol_size=6, color=color),
    )

# -------------------------
# 全局样式
# -------------------------
geo.set_global_opts(
    title_opts=opts.TitleOpts(title="h节点显示，w为省份名"),
    visualmap_opts=opts.VisualMapOpts(
        min_=anomaly_node['score'].min(),
        max_=anomaly_node['score'].max(),
        dimension=2,
        is_show=True,
        pos_top="10%",
        pos_left="right"
    ),
    tooltip_opts=opts.TooltipOpts(formatter="{b}")
)

# -------------------------
# 输出 HTML
# -------------------------
geo.render("./report/china_anomaly_dynamic.html")





