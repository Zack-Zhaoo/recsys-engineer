# 术语表

- **AUC**：随机正样本分数高于随机负样本的概率解释；不直接等于列表收益。
- **GAUC**：按用户或请求分组计算后加权聚合的 AUC，具体权重必须说明。
- **Recall@K**：前 K 个候选覆盖相关物品的比例。
- **NDCG@K**：考虑位置折损的前 K 排序质量。
- **Calibration**：预测分数与真实发生概率或价值之间的一致性。
- **Candidate Generation / Retrieval**：从大物料池产生候选，中文常称召回。
- **Pre-ranking**：在召回与精排之间的低成本筛选，常称预排或粗排。
- **Ranking**：对中等规模候选做高成本价值估计，常称精排。
- **Reranking**：考虑候选间关系、约束和列表目标生成最终 Slate。
- **Two-Tower**：用户与物品独立编码到同一向量空间，适合 ANN 检索。
- **ANN**：Approximate Nearest Neighbor，近似最近邻索引。
- **Hard Negative**：与用户或正样本较相似、但未被选择的困难负样本。
- **DLRM**：广义指使用稀疏 Embedding、稠密特征和交叉网络的深度推荐模型。
- **LRM**：Large Ranking Model，扩展判别式排序模型的容量、序列和硬件效率。
- **GR**：Generative Recommendation，把推荐目标表达为 token 或物品序列生成。
- **Semantic ID / SID**：由内容或协同表示离散化得到的多级物品 token。
- **RQ-VAE**：Residual-Quantized VAE，以多级残差量化产生离散 code。
- **NTP**：Next Token Prediction，预测下一个 token 的训练目标。
- **MFU**：Model FLOPs Utilization，实际有效模型计算相对硬件峰值的比例。
- **MoE**：Mixture of Experts，只激活部分专家以扩大容量。
- **DPO**：Direct Preference Optimization，使用偏好对直接对齐生成策略。
- **CRS**：Conversational Recommender System，对话式推荐系统。
- **Agentic Recommendation**：用记忆、规划、工具调用和反馈迭代组织推荐过程。
- **Grounding**：把语言或生成结果约束到真实、可用、可追踪的物品与操作。
- **Slate**：一次请求最终展示的有序物品列表。

