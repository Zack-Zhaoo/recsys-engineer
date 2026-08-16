# YouTube / Google 工业材料

## YouTube 官方一手

- [Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/)（2016）：经典 candidate generation + ranking 两阶段工业架构。[SRC-IND-YT-DNN-2016]
- [Recommending What Video to Watch Next](https://research.google/pubs/recommending-what-video-to-watch-next-a-multitask-ranking-system/)（2019）：多目标排序、MMoE 与选择偏差。[SRC-IND-YT-MULTITASK-2019]
- [Top-K Off-Policy Correction for a REINFORCE Recommender System](https://research.google/pubs/top-k-off-policy-correction-for-a-reinforce-recommender-system/)（2019）：在百万级动作空间中处理日志策略偏差并做在线探索。[SRC-IND-YT-OFFPOLICY-2019]

## 用户提供的中文解读

- [[推荐] CIKM'21｜谷歌：推荐中的自监督对比学习](https://zhuanlan.zhihu.com/p/457631771)：中文梳理 Feature/Interaction Masking 与对比学习。[SRC-IND-YT-SSL-ZHIHU-A]
- [谷歌在长尾推荐中的自监督多任务应用](https://zhuanlan.zhihu.com/p/701733133)：同一论文的另一篇中文解读。[SRC-IND-YT-SSL-ZHIHU-B]
- [原始论文：Self-supervised Learning for Large-scale Item Recommendations](https://arxiv.org/abs/2007.12865)：Google 团队在商业 app-to-app 推荐系统上的工作。[SRC-IND-GOOGLE-SSL-2021]

归属纠正：两篇知乎文章解读的是同一篇 Google 论文；原论文没有把生产场景声明为 YouTube，因此不能用它们证明 YouTube 的线上实现。
