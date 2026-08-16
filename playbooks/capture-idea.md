# 捕获推荐灵感

先读 [灵感孵化与实验进化](../perspective/idea-and-experiment-loop.md)。记录与立即执行是两件事。

## 触发

用户明确说“记录/保存/记下这个想法”，或明确把某段内容称为自己的推荐灵感。

## 记录前整理

保留用户原话，并补一个中性标题。只做最少结构化：

- 灵感核心与触发背景；
- 所属漏斗、范式和主题；
- 当前问题/假设；
- 可能反例与未知项；
- 当前系统的场景适配度与预计实现成本；
- 来源归属：通常是 `user` 或 `co-developed`；
- 新颖性状态固定为 `unverified`，除非完成检索。

不要为了显得完整而代写不存在的实验结果或声称“业界首创”。

## 写入

先运行 `python3 scripts/manage_workspace.py record-idea --help`，再用 `record-idea`。长内容可先整理成临时纯文本参数；不要手工破坏 JSON 索引。

- 高适配、低成本：传入 `--scenario-fit high --implementation-cost low`，默认进入 `incubating`，复看日期为七天后；需要时用 `--review-after YYYY-MM-DD` 改为数天后。
- 低适配或高成本：记录为长期灵感，不强行创建 TODO。
- 信息不足：保持 `captured`，以后用 `update-idea` 补充分流字段。

## 回显

返回 idea ID、标题、保存位置、核心假设、当前分流、复看日期和仍需验证的问题。
