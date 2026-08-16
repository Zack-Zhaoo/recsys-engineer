# 学习推荐系统

先读 [作者学习与成长理念](../perspective/learning-philosophy.md)。学习目标是建立业务、数据和系统判断，不是追逐模型清单。

## 1. 定位起点

读取 `workspace/mastery.json`。若模块是 `unassessed`，用 3–5 个问题或一个小案例确认基础，不把自信程度等同于真实能力。

## 2. 选择路径

- 新手：推荐的产业位置 → 机器学习/DLRM 基础 → 召回 → 排序 → 重排 → 数据/实验 → 产品与端到端设计 → 前沿。
- 单模块工程师：补相邻模块契约、反馈闭环与线上实验，再进入前沿。
- 资深研究者：从前沿地图选择问题，回到漏斗职责、真实业务问题、等成本 Baseline 和技术认知增量。

路径详见 [学习路径](../knowledge/core/learning-paths.md)。

## 3. 每个主题的学习闭环

按顺序让学习者完成：说明业务价值、定位漏斗、画输入输出、手算/实现最小例子、指出失败模式、选择指标、做数据切片、设计一次实验。答不出来时补对应知识，不一次灌输全部内容。

## 4. 更新能力

只有出现证据才更新 mastery：

- `aware`：能识别概念与位置；
- `explain`：能解释机制与边界；
- `apply`：能实现或诊断；
- `design`：能权衡端到端方案；
- `research`：能提出可证伪新问题并做严谨验证。

用 `python3 scripts/manage_workspace.py set-mastery ...` 写入证据。一次问答通常最多提升一级。

除算法模块外，持续观察 `core.industry-positioning`、`core.product-thinking`、`core.data-analysis`、`core.system-thinking`、`engineering.lifecycle-operations` 和 `research.frontier-judgment`。不因会讲最新模型而自动判定具备产品或系统能力。

## 5. 输出

给出当前判断、已掌握证据、下一主题和一个可检验练习；若更新了 workspace，明确回显。
