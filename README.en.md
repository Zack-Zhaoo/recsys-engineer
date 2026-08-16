# recsys-engineer

[中文](README.md)

[![validate](https://github.com/Zack-Zhaoo/recsys-engineer/actions/workflows/validate.yml/badge.svg)](https://github.com/Zack-Zhaoo/recsys-engineer/actions/workflows/validate.yml)

I built this recommender-systems skill together with AI, notebook feature and all, distilling a little of what I know. It covers a foundational learning path for recommender systems plus some more advanced material, and it carries my own views on a number of questions. I believe both newcomers and working algorithm engineers will find something useful in it. This is the first version. You're welcome to follow it, download it, use it, and send me your feedback. I'll keep iterating on it for the long haul.

---

When you use an AI to answer questions about recommender systems, the recurring difficulty is judging how much a given conclusion can be trusted. The same figure might come from a paper's experiment, from a company blog describing its own work, or simply from the model's guess. Without a source, an answer like that cannot carry a technical decision.

This Skill puts an evidence grade on every conclusion: stable consensus, paper report, company report, synthesized judgment, author opinion, or open hypothesis. Anything touching industrial gains is always written as "the paper/company reports," never as verified fact.

The 74 papers and 43 company engineering articles it collects all carry links. Company articles are further graded as first-party official, team-authored, or secondary commentary, and secondary commentary serves only as a reading aid. It cannot on its own support a claim about a first, a deployment, or a reported gain.

Knowledge is fixed at 2026-08-01, with no web retrieval. Asked about recent work, it states that boundary first rather than treating anything after the cutoff as known.

Everything inside is written in Chinese and it answers in Chinese. This page is translated so people can find it.

## Install

This is a standard Agent Skill directory and is not tied to one client. The commands below use Claude Code; other clients that support Skills load the same directory, or the packaged `.skill` file, their own way.

```bash
git clone https://github.com/Zack-Zhaoo/recsys-engineer.git ~/.claude/skills/recsys-engineer
```

Windows:

```powershell
git clone https://github.com/Zack-Zhaoo/recsys-engineer.git "$env:USERPROFILE\.claude\skills\recsys-engineer"
```

Under `~/.claude/skills/` it works in every project; clone into a project's `.claude/skills/` to scope it there.

If you need an archive instead, run `python3 scripts/build_skill_package.py` after cloning; the output lands in `dist/`.

Then check it:

```bash
python3 ~/.claude/skills/recsys-engineer/scripts/validate_skill.py
```

`Validation passed:` means nothing is missing or broken. The script is read-only, makes no network calls, and walks the directory structure, every internal link, and the mapping between citation IDs and the source catalogs.

Restart your client and ask something. If the answer places the method in the funnel, covers sampling-bias correction, and says what to watch on the index side, it's working.

## What to ask

Plain language, no commands to memorize:

- Plan me a path to learn recsys from scratch
- Design a cold-start retrieval scheme for short video
- CTR is up but watch time is down after release, where do I look
- What actually separates LRM, generative rec, and agentic rec
- Analyze this paper, is it worth following
- Record this idea: allocate diversity budget by uncertainty

The last one takes a different path. `workspace/` belongs to whoever installed it and holds mastery assessments, settled positions, and original ideas. Entries keep their original wording and a "not yet verified" marker, with nothing inflated on the author's behalf. Version updates never overwrite it.

The rest read from `knowledge/` (public evidence) and `perspective/` (author judgment, labeled separately from fact).

## Coverage

Retrieval, pre-ranking, ranking, re-ranking and policy, feedback loops, data and sampling, features and embeddings, training and serving, evaluation and experimentation, reliability and governance. Five frontier tracks: large ranking models, generative recommendation, LLMs in recommendation, agentic recommendation, multimodal.

Papers run 2009 to 2026 in three tiers: classic prototypes, industrial variants, frontier work. The middle tier is the one that usually gets dropped. PLE, PEPNet, SIM, TWIN and similar are what actually ships, and they rarely appear on reading lists.

Company articles cover Meta, YouTube/Google, Meituan, ByteDance, Alibaba, Tencent, Kuaishou, Ximalaya.

## Upgrading

**Don't use `git pull`.** `workspace/` holds user data, so pulling conflicts and copying over the top wipes it. Use this:

```bash
python3 <new version>/scripts/upgrade.py --target ~/.claude/skills/recsys-engineer --apply
```

It backs `workspace/` up to a timestamped directory, replaces only the knowledge and perspective layers, and migrates existing mastery assessments onto the new module list. Then it validates and compares before/after counts, warning if anything dropped.

Without `--apply` it's a dry run.

## Extending it

The license permits refreshing or rewriting this snapshot. Two tools under `scripts/`:

```bash
python3 scripts/refresh_snapshot.py --date 2027-02-01   # move the cutoff, and audit whether content keeps up
python3 scripts/build_skill_package.py                  # package; won't build if validation fails
```

`refresh_snapshot.py` blocks one specific mistake: moving the date does not make the knowledge newer. It reports how recent the newest catalog entry actually is and how large the gap to the new cutoff has become.

## License

Content is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), `scripts/` is MIT. Use it, modify it, sell it, redistribute it. Attribution is all that's required. Whatever you produce with it is entirely yours, with no attribution or revenue share. Details in [LICENSE.md](LICENSE.md).

Papers and company articles cited under `knowledge/` are not part of this project. Only links, metadata, and a one-line summary are stored, and copyright remains with their authors.

## Author

Lili Dashixiong (力力大师兄), algorithm engineer at Kuaishou, JD.com, and Baidu.

Questions, corrections, collaboration: brolili@163.com
