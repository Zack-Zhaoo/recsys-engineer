# 美团工业文章

以下均来自美团技术团队官方站点。

- [美团搜索粗排优化的探索与实践](https://tech.meituan.com/2022/08/11/Coarse-Ranking-Exploration-Practice.html)（2022）：粗排样本选择偏差、精排结果/分数/表征蒸馏、对比学习，以及效果—延迟联合 NAS。[SRC-IND-MT-COARSE-2022]
- [多场景多任务学习在美团到店餐饮推荐的实践](https://tech.meituan.com/2023/03/23/recommendation-multi-scenario:task.html)（2023）：HiNet 用场景层和任务层分层提取共享/特有信息，讨论负迁移和多场景部署。[SRC-IND-MT-HINET-2023]
- [MTGR：美团外卖生成式推荐 Scaling Law 落地实践](https://tech.meituan.com/2025/05/19/Meituan-Generative-Recommendation.html)（2025）：保留 DLRM 交叉特征的 HSTU 混合架构、用户粒度压缩、动态掩码及训练/推理引擎。[SRC-IND-MT-MTGR-2025]

用户列表中的粗排链接重复一次，本库已去重。MTGR 的论文和训练系统另见 [SRC-MTGR-2025]、[SRC-MTGENREC-2025]。

## 2026 年新增

- [美团搜索3.0：LLM 语义表征在排序模型的探索与应用](https://tech.meituan.com/2026/08/20/01-meituan-Query-3.0.html)（2026）：把 LLM 定位成特征供给方而非决策者，语义相似度作为一路特征接入既有排序模型，排序模型与漏斗都不动。分三期推进，先证明信号有效，再把在线开销压到可接受，最后扩大适用范围并改进接入方式。公司报告称各期订单提升在千分之几量级，并明确给出了在线延迟开销。文中记录的失败尝试比成功路径更值得读，包括复杂提示不敌简洁陈述、补充结构化属性反而使离线指标下降、表征跨阶段直接复用导致覆盖率不足。接入位置的四方案对比和文末五条经验沉淀值得直接查原文；它是"如何把大模型能力接进成熟工业系统"的完整示范，参见 [侵入性谱系](../../paradigms/llm-in-recommendation.md)。[SRC-IND-MT-SEARCH3-2026]
- [KDD'26 学术论文精选及 KDD Cup'26 DataAgents 冠军思路](https://tech.meituan.com/2026/08/13/KDD-2026-meituan-papers.html)（2026）：八篇论文的官方导读，其中六篇与推荐、搜索或广告相关。可顺此追两条线索，一是免对齐的多场景工业推荐基础模型，二是面向本地生活场景的 Agentic 搜索评测集；生成式推荐的分布式训练系统已单独收录于论文目录。合集本身只作导读，不单独支撑任何结论。[SRC-IND-MT-KDD26-2026]
- [Agent 评测漫谈](https://tech.meituan.com/2026/08/07/Agent-Evaluation.html)（2026）：把 Agent 评测拆成结果、过程、效率与风险四层，主张评的是模型加系统而非模型本身，轨迹评测与响应评测并重。真正可操作的部分在评测运营，包括把模糊标准拆成二值判断、按未知率迭代直至人机一致率达标、以及从少量关键指标逐步扩充的案例飞轮。[SRC-IND-MT-AGENT-EVAL-2026]
