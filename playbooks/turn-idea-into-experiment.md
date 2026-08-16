# 灵感转实验

先读 [灵感孵化与实验进化](../perspective/idea-and-experiment-loop.md)。实验优先验证适配后的核心机制，不默认完整复现论文。

## 形成可证伪假设

写成：“在场景 S 和约束 C 下，用 X 改变机制 M，相对 Baseline B，使主指标 Y 至少改善 δ，同时护栏 H 不恶化超过 ε。”

## 最小实验包

- 数据和时间切分；
- 工业当前 Baseline、最接近论文 Baseline、等成本 Baseline；
- 最小原型，不先构建完整平台；
- 主指标、切片、成本和失败阈值；
- 能拆分关键机制的 2–4 个消融；
- 资源预算、执行顺序和停止规则。
- 预期改变的中间信号，以及若指标不好时第一轮归因路径。

## 推荐阶段桥接

明确实验位于召回、预排、排序、重排还是 Agent 编排层。若跨层，分别设置模块成功条件和端到端成功条件，避免上游离线提升被下游吞掉。

## 写回

实验方案追加到 idea card，状态设为 `experiment-ready`；执行后改为 `experimenting`。不要在没有结果时标记 `validated`，不要把上线等同于 `adopted`，直到方案进入稳定系统。

实验结束后执行 [实验复盘](review-experiment.md)，至少写回 `actual_result`、`diagnosis`、`knowledge_gained` 和 `decision`。
