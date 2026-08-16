# recsys-engineer

[English](README.en.md)

[![validate](https://github.com/Zack-Zhaoo/recsys-engineer/actions/workflows/validate.yml/badge.svg)](https://github.com/Zack-Zhaoo/recsys-engineer/actions/workflows/validate.yml)

问 AI 推荐系统的问题,答案读起来都挺顺,但你分不清它在说什么级别的话。

它说"某某方法能提升 3%",这可能是论文里的数字,可能是公司博客的自述,也可能是它顺手编的。它说"业界普遍这么做",又是哪家公司,哪一年。想查出处也查不到。这种回答拿去开会讲讲可以,拿去定方案心里没底。

这是一个推荐系统的 Agent Skill,给每条结论都标了证据等级,分成稳定共识、论文报告、公司报告、综合判断、作者观点、开放假设六种。凡是提到工业收益,一律写成"论文/公司报告称",不把公司自述写成已验证的事实。

74 篇论文和 43 篇公司技术文章都带链接。公司文章再分官方一手、团队署名、二手解读三级。知乎那类解读只作导读,不能单独支撑"首次""已上线""涨了多少"这类声明。

知识截止 2026-08-01,不联网,并且认这个账。问最新进展时它会先说明这是快照边界,而不是把之后的事当成已知的讲。

安装后直接用中文提问。

## 安装

这是标准的 Agent Skill 目录,不绑定某一个客户端。下面以 Claude Code 为例,其他支持 Skill 的客户端按各自的方式加载同一个目录,或加载打包好的 `.skill` 文件。

```bash
git clone https://github.com/Zack-Zhaoo/recsys-engineer.git ~/.claude/skills/recsys-engineer
```

Windows 用 PowerShell。

```powershell
git clone https://github.com/Zack-Zhaoo/recsys-engineer.git "$env:USERPROFILE\.claude\skills\recsys-engineer"
```

放在 `~/.claude/skills/` 下所有项目都能用。只想在某个项目里用,就 clone 到该项目的 `.claude/skills/` 下。

需要压缩包的话,克隆后执行 `python3 scripts/build_skill_package.py`,产物在 `dist/` 下。

安装后先校验一遍。

```bash
python3 ~/.claude/skills/recsys-engineer/scripts/validate_skill.py
```

输出 `Validation passed` 说明文件没缺没坏。脚本只读、不联网,会把目录结构、所有内部链接、引用编号与来源目录的对应关系查一遍。

最容易卡住的一步是忘了重启客户端。重启之后问一句"双塔召回的负采样怎么选",答案里如果带上它在哪一层漏斗、采样偏差怎么校正、索引侧要看什么,就是生效了。

## 能问什么

直接说人话,不用记命令。

- 我想从零系统学推荐,帮我规划路径
- 帮我设计一个短视频冷启动的召回方案
- 上线后 CTR 涨了但人均时长跌了,从哪查
- LRM、生成式推荐、Agentic 到底差在哪
- 帮我分析这篇论文,值不值得跟进
- 记下这个想法,用不确定性分配多样性预算

最后一条走另一条路径。`workspace/` 是使用者自己的区域,存能力评估、稳定观点和原创想法,记录时保留原始表达和尚未验证的标记,不替人夸大。版本更新不会覆盖它。

其余问题读 `knowledge/` 里的公开证据,以及 `perspective/` 里的作者判断。后者会单独标注,不和事实混写。

## 覆盖范围

召回、预排、精排、重排与策略、反馈闭环、数据与采样、特征与 Embedding、训练与 Serving、评估与实验、可靠性与治理。前沿五条线是 Large Ranking Model、生成式推荐、LLM 推荐、Agentic 推荐和多模态。

论文从 2009 排到 2026,分经典原型、工业变体、前沿工作三层。中间那层最容易被漏掉。PLE、PEPNet、SIM、TWIN 这些实际在用的东西,论文清单里经常没有。

公司文章覆盖 Meta、YouTube/Google、美团、字节、阿里、腾讯、快手、喜马拉雅。

## 升级

**别用 `git pull`。** `workspace/` 里是使用者的数据,拉取会冲突,整包覆盖会清空。用下面这条。

```bash
python3 <新版本目录>/scripts/upgrade.py --target ~/.claude/skills/recsys-engineer --apply
```

它先把 `workspace/` 备份到带时间戳的目录,只替换知识与视角两层,再把已有的能力评估迁到新版本的模块表上。跑完自动校验,并对比升级前后的条目数,任何一项减少都会报警。

不加 `--apply` 是空跑,只报告会发生什么。

## 扩展与续期

许可允许基于这份快照续期或改写。两个工具在 `scripts/` 下。

```bash
python3 scripts/refresh_snapshot.py --date 2027-02-01   # 推进截止日,并审计内容是否跟得上
python3 scripts/build_skill_package.py                  # 打包,校验不过不出包
```

`refresh_snapshot.py` 会拦一件事。改日期不等于知识变新,它会报出来源目录里最新条目的时间,以及离新截止日差了多远。

## 许可

内容 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-Hans),`scripts/` MIT。可以使用、修改、商用、再分发,保留署名即可。用它产出的成果完全归使用者,无需署名或分成。细则见 [LICENSE.md](LICENSE.md)。

`knowledge/` 中引用的论文和公司文章不属于本项目内容,只存链接、元数据和一句话摘要,著作权归原作者。

## 作者

力力大师兄,先后在快手、京东、百度担任算法工程师。

问题、勘误、协作都可以发到 brolili@163.com。
