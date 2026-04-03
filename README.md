# 异常流向检测与可视化

本项目用于检测区域之间的异常流向，并对异常流向进行可视化展示，包括异常流向地图和异常流向的时间趋势图。

---
## 环境安装

- Python 3.10 及以上版本
- Python 依赖库

安装依赖：pip install numpy pandas pyecharts

## 数据准备
确保data.xlsx在目录下

## 运行程序

run.bat

## 输出结果

程序运行完成后会生成以下文件：

- edes.csv
- anomaly_result.json
- report/
  - 异常流向图 (HTML)
  - plots/
    - 月度趋势图 (HTML)
