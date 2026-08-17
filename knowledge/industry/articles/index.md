# 工业文章索引

本目录收录 2026-08-01 之前的公司工程文章、团队公众号文章、官方研究页面和少量高质量中文解读。只保存链接、证据级别与短摘要，不复制原文。

## 按公司读取

- [Meta](meta.md)：Instagram 漏斗、模型治理、统一 GPU 召回。
- [YouTube / Google](youtube.md)：候选生成、多任务排序、Off-policy/RL，以及两篇需纠正归属的中文解读。
- [美团](meituan.md)：粗排、跨场景多任务、MTGR 生成式排序与训推。
- [字节跳动](bytedance.md)：RankMixer、TokenMixer-Large 的中文解读与原论文配对。
- [阿里巴巴](alibaba.md)：长序列、LRM、RecGPT/RecBot、搜索 Agent 和长期价值。
- [腾讯](tencent.md)：生成式广告、统一多域序列、LLM+GNN 召回。
- [快手](kuaishou.md)：生成式推荐/搜索/广告、Semantic ID + RL、推理推荐与研发 Agent。
- [喜马拉雅](ximalaya.md)：音频生成式/交互式推荐，以及广告召回、排序和漏斗实践。

## 按问题读取

| 问题 | 优先材料 |
|---|---|
| 多阶段漏斗与召回 | Meta Explore、YouTube DNN、喜马广告漏斗/召回 |
| 粗排 | 美团搜索粗排 |
| 多任务与多场景 | YouTube multitask、HiNet、TokenFormer |
| LRM 与 Scaling | RankMixer/TokenMixer 解读、阿里 EST/SSR、美团 MTGR |
| 生成式推荐/搜索/广告 | MTGR、腾讯 GPR、快手 OneSearch/GR4AD/RaG、喜马 GR |
| Agentic 推荐 | RecGPT/RecBot、快手 AgentX/OneReason、喜马交互式推荐 |
| 训练、Serving 与治理 | Meta 1000 models/SilverTorch、美团 MTGR |

## 使用纪律

1. 先用官方一手或团队署名材料确认系统事实，再用二手解读帮助中文理解。
2. 公司文章中的收益属于公司自报；记录场景、基线、周期和是否全量。
3. 同一论文的多篇解读不算独立证据。
4. 文章分组按讨论对象，不代表发布者就是该公司。
5. 完整结构化元数据见 [文章目录](catalog.yaml)。

需要决定是否精读、如何看团队与作者背景、以及如何分开评价可信度与启发价值时，使用 [作者研究评价方法](../../../perspective/research-evaluation.md)。
