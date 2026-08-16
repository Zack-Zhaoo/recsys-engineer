# Meta 工业文章

以下均为 Meta Engineering 官方一手材料。

## 推荐漏斗

- [How Instagram suggests new content](https://engineering.fb.com/2020/12/10/web/how-instagram-suggests-new-content/)（2020）：从候选生成和候选选择解释 Instagram Suggested Posts，并讨论连接内/连接外推荐。[SRC-IND-META-SUGGESTED-POSTS-2020]
- [Scaling the Instagram Explore recommendations system](https://engineering.fb.com/2023/08/09/ml-applications/scaling-instagram-explore-recommendations-system/)（2023）：完整拆解 retrieval、first-stage ranking、second-stage ranking 和 final reranking，包含双塔、ANN、蒸馏与多任务打分。[SRC-IND-META-EXPLORE-2023]

## 平台与召回演进

- [Journey to 1000 models: Scaling Instagram's recommendation system](https://engineering.fb.com/2025/05/21/production-engineering/journey-to-1000-models-scaling-instagrams-recommendation-system/)（2025）：重点不是新模型结构，而是模型注册、发布自动化、稳定性指标与 SLO。[SRC-IND-META-1000-MODELS-2025]
- [SilverTorch: Index as Model](https://engineering.fb.com/2026/05/26/ml-applications/silvertorch-index-as-model-new-retrieval-paradigm-recommendation-systems/)（2026）：把索引、过滤、打分和 reranking 表达为统一 PyTorch 模型，关注 GPU 召回、版本一致性和系统吞吐。[SRC-IND-META-SILVERTORCH-2026]

补充论文：HSTU 见 [SRC-HSTU-2024]，Kunlun 见 [SRC-KUNLUN-2026]。博客中的数字仍属于 Meta 自报。
