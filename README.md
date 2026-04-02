# 异常流向检测与可视化

本项目用于检测区域之间的异常流向，并对异常流向进行可视化展示，包括异常流向地图和异常流向的时间趋势图。

---

## 项目流程

程序按以下步骤依次执行：

### 0. 数据准备
确保data.xlsx在目录下

### 1. 数据处理

运行：process.py 生成文件：edes.csv

---

### 2. 时间异常检测

运行：time_anomaly_test.py 生成文件：anomaly_result.json

---

### 3. 异常流向可视化

运行：plot_flow.py 在目录 `/report` 下生成异常流向图。

---

### 4. 异常流向趋势可视化

运行：plot_tendency.py 在目录 `/report/plots` 下生成异常流向的月度趋势图。

---

## 运行方式

在 **Windows 系统**中，在项目根目录运行：run.bat
或者直接 **双击 `run.bat` 文件**。

该脚本会自动按顺序执行以下程序：
process.py
→ time_anomaly_test.py
→ plot_flow.py
→ plot_tendency.py


---

## 依赖环境

- Python 3.10 及以上版本
- Python 依赖库

安装依赖：pip install numpy pandas pyecharts

---

## 输出结果

程序运行完成后会生成以下文件：

- edes.csv
- anomaly_result.json
- report/
  - 异常流向图 (HTML)
  - plots/
    - 月度趋势图 (HTML)
