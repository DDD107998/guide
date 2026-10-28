# 宁夏大学鑫启网安俱乐部 · 入门教程

本仓库为宁夏大学鑫启网安俱乐部（XinQi Cyber Club）的体系化教程正文，面向新成员与外部协作者。

教程按能力递进组织，涵盖基础工具链、实验环境、协作流程、代码规范与竞赛入门五个板块。

---

## 一、阅读路线

| 顺序 | 章节 | 内容 | 预计耗时 |
| :-- | :-- | :-- | :-- |
| 0 | [00 加入社团流程](00-加入社团流程.md) | 从注册账号到完成首次变更请求的完整步骤 | 45 分钟 |
| 1 | [01 组织概况](01-组织概况.md) | 组织定位、业务方向、成员构成与准入要求 | 5 分钟 |
| 2 | [02 基础环境搭建](02-基础环境搭建.md) | Git、运行时、编辑器与终端配置 | 30 分钟 |
| 3 | [03 安全实验环境](03-安全实验环境.md) | 虚拟机、靶场部署、网络隔离与合规边界 | 60 分钟 |
| 4 | [04 Git 与 GitHub 协作](04-Git与GitHub协作.md) | 分支模型、提交规范、变更请求与评审 | 40 分钟 |
| 5 | [05 代码与文档规范](05-代码与文档规范.md) | 目录结构、命名、注释、格式化与文档体例 | 20 分钟 |
| 6 | [06 CTF 入门](06-CTF入门.md) | 五方向知识结构与学习路径 | 30 分钟 |
| 7 | [07 常见问题](07-常见问题.md) | 高频故障与处理方式 | 按需查阅 |
| 8 | [08 支持渠道](08-支持渠道.md) | 提问规范与响应时限 | 按需查阅 |

建议按序完成第 0 至第 4 章。第 5 至第 6 章可在参与实际项目或备赛时查阅。

---

## 二、完成标准

加入社团的判定标准为：

1. 完成[加入社团申请](https://github.com/NingXia-XinQiCyberClub/.github/issues/new?template=join.yml)工单中的全部条目
2. 成功 fork 并克隆任一组织仓库，完成一次变更请求的合并
3. 在 [Discussions](https://github.com/NingXia-XinQiCyberClub/.github/discussions) 完成自我介绍

## 三、入门任务

以下工单构成新成员的入门任务集，按难度递增排列。任务均以文档修订为主，不涉及复杂代码，目的是在真实仓库中完成一次完整的协作流程。

| 顺序 | 工单 | 训练目标 | 预计耗时 |
| :-- | :-- | :-- | :-- |
| 1 | [#4 补充 Windows 下 GBK 文件乱码的处理条目](https://github.com/NingXia-XinQiCyberClub/guide/issues/4) | 补充文档章节，练习定位既有内容与保持体例一致 | 1 小时 |
| 2 | [#2 校对第 2 章 macOS 与 Linux 命令](https://github.com/NingXia-XinQiCyberClub/guide/issues/2) | 实际验证命令，练习以事实为依据修订文档 | 2 小时 |
| 3 | [#1 为第 6 章补充各方向练习题清单](https://github.com/NingXia-XinQiCyberClub/guide/issues/1) | 检索与筛选外部资料，练习信息组织与来源标注 | 3 小时 |
| 4 | [#3 补充 LICENSE 文件](https://github.com/NingXia-XinQiCyberClub/guide/issues/3) | 了解许可证类型，练习与维护者确认决策 | 1 小时 |

任务执行要求：

1. 领取任务前先在工单内回复，说明计划与预计完成时间，避免多人重复处理
2. 按[贡献指南](https://github.com/NingXia-XinQiCyberClub/.github/blob/main/CONTRIBUTING.md)的流程 fork、创建分支、提交与变更请求（成员账号只读，不向组织仓库直接推送）
3. 变更请求中须引用对应工单编号，格式为 `Closes #<编号>`
4. 评审意见的处理方式为在原分支追加提交，不关闭后重新发起

全部工单同时聚合于本仓库的 [`/contribute`](https://github.com/NingXia-XinQiCyberClub/guide/contribute) 页面。

---

## 四、相关文档

| 文档 | 用途 |
| :-- | :-- |
| [CONTRIBUTING.md](https://github.com/NingXia-XinQiCyberClub/.github/blob/main/CONTRIBUTING.md) | 协作流程的规范性文件，本教程第 4 章为其教学版本 |
| [CODE_OF_CONDUCT.md](https://github.com/NingXia-XinQiCyberClub/.github/blob/main/CODE_OF_CONDUCT.md) | 行为准则 |
| [SECURITY.md](https://github.com/NingXia-XinQiCyberClub/.github/blob/main/SECURITY.md) | 安全缺陷上报政策 |
| [SUPPORT.md](https://github.com/NingXia-XinQiCyberClub/.github/blob/main/SUPPORT.md) | 提问规范与响应时限 |

规范文件与教程内容冲突时，以规范文件为准。

---

## 五、修订说明

本教程采用普通 Markdown 维护，修订通过变更请求进行。发现表述错误、命令失效或环境描述过时，应提交变更请求并注明依据。

各章节末尾标注适用环境与最近校订日期，超出一年未校订的内容应重新验证。
## 许可证

本仓库文档采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) 协议开源，详见 LICENSE 文件。
