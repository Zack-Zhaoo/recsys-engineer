# 学习路径

## 从零入门

1. 先理解推荐在互联网流量、增长、体验、商业化和 AI 个性化中的位置。
2. 读 `foundations.md`，掌握机器学习、隐式反馈和曝光偏差。
3. 读 `funnel/end-to-end.md`，建立线上漏斗地图。
4. 依次学习召回、排序、重排，不先追求最新模型。
5. 学数据采样、产品指标、离线评估和 A/B，理解“模型好”如何成立。
6. 再进入 LRM、GR、LLM、Agentic、Auto RS 和 RS in AI。

验收标准：能用自己的话解释为什么推荐不能只看点击率，能画出候选数和计算成本逐层变化的链路。

完整培养理念见 [作者学习与成长理念](../../perspective/learning-philosophy.md)。

## 经典读物清单

下列材料构成进入前沿之前的共同底座。它们的价值不在结构本身，而在于每一篇都第一次把某个约束讲清楚。链接与元数据见 [论文来源目录](../sources/catalog.yaml)。

| 阶段 | 起点材料 | 该读它的理由 |
|---|---|---|
| 基础与目标 | BPR、NCF [SRC-BPR-2009] [SRC-NCF-2017] | 隐式反馈为什么要做成相对偏好，而不是评分回归 |
| 召回 | DSSM、MIND、TDM [SRC-DSSM-2013] [SRC-MIND-2019] [SRC-TDM-2018] | 双塔的表达力边界，以及检索为何被内积形式限制 |
| 召回训练 | Sampling-Bias-Corrected [SRC-SAMPLING-BIAS-2019] | 采样分布如何改变分数含义，校正项从哪来 |
| 索引与 Serving | HNSW、Faiss [SRC-HNSW-2016] [SRC-FAISS-2017] | 近似检索的质量—内存—吞吐三角 |
| 预排 | COLD [SRC-COLD-2020] | 把算力预算写进优化目标，而不是先建模再砍成本 |
| 排序 | Wide & Deep、DIN、DIEN、DCN V2 [SRC-WIDE-DEEP-2016] [SRC-DIN-2018] [SRC-DIEN-2019] [SRC-DCNV2-2021] | 记忆与泛化的分工，目标感知的兴趣激活 |
| 序列建模 | SASRec、BERT4Rec [SRC-SASREC-2018] [SRC-BERT4REC-2019] | 序列推荐的两种训练范式及其评测争议 |
| 多目标 | MMoE、ESMM [SRC-MMOE-2018] [SRC-ESMM-2018] | 任务冲突的结构化处理，以及后置转化的样本空间问题 |
| 重排与策略 | DPP、LinUCB [SRC-DPP-2018] [SRC-LINUCB-2010] | 多样性如何变成可解的目标，探索如何被形式化 |
| 偏差与闭环 | Recommendations as Treatments、Degenerate Feedback Loops [SRC-REC-TREATMENTS-2016] [SRC-DEGENERATE-LOOP-2019] | 缺失非随机的标准形式化，以及闭环退化的机制 |
| 评估与实验 | CUPED [SRC-CUPED-2013] | 不加流量提高实验灵敏度的通用手段 |
| 工程与表示 | DLRM、Item2Vec [SRC-DLRM-2019] [SRC-ITEM2VEC-2016] | 稀疏表主导的训练/Serving 切分，ID 表示的起点 |
| 多模态 | CLIP [SRC-CLIP-2021] | 可复用跨模态表示的能力边界与偏好错配 |

读完一篇请回答：它解决的约束是什么、在漏斗哪一层生效、用什么指标验证、今天是否仍成立。记住结构名不构成掌握，见 [作者原则第 7 条](../../perspective/principles.md)。

## 工业变体清单

原型论文说明“这件事可以做”，变体说明“在真实约束下它被改成了什么样”。日常工程里被反复复用的常常是后者，面试和方案评审也更常问这一层。变体不是原型的升级版，读的时候要抓住它放弃了什么、换回了什么。

| 主题 | 从原型到变体 | 变体多解决了什么 |
|---|---|---|
| 特征交叉 | Wide & Deep → DeepFM → xDeepFM → AutoInt [SRC-DEEPFM-2017] [SRC-XDEEPFM-2018] [SRC-AUTOINT-2019] | 去掉人工交叉、把交叉提到向量级、让交叉权重可学 |
| 多任务 | MMoE → PLE [SRC-PLE-2020] | 用渐进分层的共享/专属专家正面处理跷跷板 |
| 转化链路 | ESMM → AITM [SRC-AITM-2021] | 多步转化之间是有序依赖，不是并列的独立头 |
| 多场景 | 单场景排序 → STAR [SRC-STAR-2021] | 同一目标不同分布：共享中心参数加场景专属参数 |
| 参数个性化 | LHUC → POSO → PEPNet [SRC-LHUC-2016] [SRC-POSO-2021] [SRC-PEPNET-2023] | 主干不变、用先验生成乘性系数，延迟可控地吃下人群差异 |
| 门控家族旁支 | MaskNet [SRC-MASKNET-2021] | 实例引导的乘法 mask，与上一行同源不同用法 |
| 长序列 | DIN/DIEN → MIMN → SIM → TWIN [SRC-MIMN-2019] [SRC-SIM-2020] [SRC-TWIN-2023] | 压缩成可增量更新的状态 → 检索相关子序列 → 消除检索与精排的度量不一致 |
| 多兴趣召回 | MIND → ComiRec [SRC-COMIREC-2020] | 兴趣数量与多样性权衡变成可控参数 |
| 双塔落地 | DSSM → Facebook EBR [SRC-FB-EBR-2020] | 难负例、样本分布、索引调优与下游耦合的完整工程账 |
| 联合索引 | TDM → Deep Retrieval [SRC-DEEP-RETRIEVAL-2020] | 用可学习路径结构替代树，降低索引重建耦合 |
| 预排蒸馏 | 通用蒸馏 → Rocket Launching → COLD [SRC-ROCKET-2018] | 轻网络与教师联合训练、共享底层参数 |
| 位置偏差 | 直接用曝光标签 → PAL [SRC-PAL-2019] | 训练时分离位置与相关性，线上只用相关性打分 |

关于快手 PPNet：它在工业交流中被广泛提及，但公开可引用的完整表述以 PEPNet 为准，思想源头是语音自适应的 LHUC。用博客或口头介绍支撑“某公司首次/收益多少”的强声明不成立，见 [证据规则](../sources/evidence-policy.md)。

## 召回工程师

主线：协同过滤 → Two-Tower → 负采样 → ANN → 多兴趣 → 多路融合 → 生成式召回。

重点能力：候选覆盖、索引更新、Embedding 一致性、难负样本、长尾和线上召回归因。

## 排序工程师

主线：特征交叉 → 行为序列 → 多任务 → Calibration → 长序列 → MoE → LRM/token 化。

重点能力：样本口径、目标设计、特征新鲜度、离线线上一致性、GPU 利用率和 Serving。

## 重排与策略工程师

主线：Listwise → 多样性/打散 → 约束优化 → Slate → Bandit/RL → Agentic 编排。

重点能力：候选间相互作用、长期目标、安全约束、可解释策略和回滚。

## 生成式推荐研究者

先掌握召回、序列推荐和离散表示，再学习 Semantic ID、RQ-VAE、自回归解码、session-wise generation、偏好对齐和工业 Serving。

## Agentic 推荐研究者

先掌握现有漏斗和评估，再学习意图、记忆、规划、工具、状态机、多 Agent 和过程级评估。始终明确 Agent 改变的下一步动作。

## Auto RS 研究者

先掌握数据口径、实验平台、诊断、各层模块契约和治理，再研究自动假设、特征/模型修改、A/B 归因和受控自治。不要把自动调参直接称为系统自进化。

## RS in AI 研究者

补齐长期记忆、工具/Agent 选择、主动交互、多目标决策和用户控制。把推荐对象从内容扩展到知识、工具、服务、任务和行动，同时保留安全与可撤销性。

## 岗位转型

- 排序 → GR：补检索、tokenization、解码和序列级评估。
- 召回 → LRM：补特征交叉、多目标、GPU 架构和长序列。
- 推荐 → Agentic：补语言模型边界、工具契约、可靠性、记忆读写和轨迹评估。
