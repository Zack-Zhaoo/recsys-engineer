# 发展已有灵感

先读 [灵感孵化与实验进化](../perspective/idea-and-experiment-loop.md)。

## 读取

从 `workspace/ideas/index.json` 定位卡片；保留原始表述，不覆盖历史。区分用户原意和本轮共同推演。

若状态为 `incubating`，先检查是否到复看日期；除非用户主动要求，不为清理 TODO 强行提前实验。查找可聚合的 `related_ideas`，区分论文原方法与针对当前系统形成的 `local_adaptation`。

## 展开八问

1. 它解决哪个真实推荐职责？
2. 现有强方法为何不足？
3. 新机制是什么，最小可实现形式是什么？
4. 在什么条件下应有效，最可能在哪失败？
5. 如何与现有漏斗、数据和 Serving 集成？
6. 哪项结果会证伪它？
7. 场景适配度和实现成本是否改变了？
8. 能否与相似 idea 合并成一次更有信息量的实验？

## 新颖性

若用户要求判断是否新颖，需要查截止快照内来源；若要最新状态，应联网并标记快照外内容。检索前状态保持 `unverified`。

## 更新

用 `update-idea` 追加进展、分流字段、关联 idea 或状态。状态按 `captured → incubating → clustered/developing → experiment-ready → experimenting → adopted/validated/rejected/archived` 演进。`validated` 表示假设获证据支持，不等于已经上线；`adopted` 才表示进入真实系统或稳定方案。
