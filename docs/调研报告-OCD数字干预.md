# 调研报告：OCD 数字干预方案全景

> 调研时间：2026-08 · 范围：GitHub 开源项目 + 全网（PubMed 临床试验、应用商店、国内外产品）
> 复现方式：`research/` 目录下的脚本与 JSON 数据

## 一、主流技术路径全景

| 路径 | 原理 | 证据强度 | 代表 |
|---|---|---|---|
| **CBT/ERP 数字疗法** | 认知重构 + 暴露反应阻止，搬到 App | ⭐⭐⭐⭐⭐ 多项 RCT | NOCD、ocd.app、Perspectives |
| **AI 对话代理** | CBT 结构化对话，陪伴式 | ⭐⭐⭐ RCT 支持 | Wysa、Woebot |
| **VR/AR 暴露疗法** | 虚拟环境分级暴露 | ⭐⭐⭐ 研究阶段 | CureOCD（开源）、C2Care |
| **神经调控（硬件）** | tDCS 微电流刺激前额叶 | ⭐⭐ 证据不足 | 英智科技（国内） |
| **追踪/日志工具** | 记录触发、冲动、ERP 训练 | ⭐⭐ 辅助性 | ERPMate、MindEase |
| **开源研究平台** | 数字表型、数据采集 | ⭐⭐⭐ 学术框架 | mindLAMP、MindLogger |

## 二、有临床证据的商业/学术产品

### 1. NOCD（treatmyocd.com）
- 美国最大 OCD 平台：治疗师对接 + 实时 ERP 工具 + 全球最大 OCD 社区
- 商业产品，偏治疗师驱动

### 2. ocd.app / GGOC（GGtude，ocd.app）
- 以色列 **Guy Doron 教授**（OCD 领域知名研究者）团队
- CBT 每日 **3-5 分钟微训练**，22 篇论文背书（10 项 RCT）
- 被国际强迫症基金会（IOCDF）评为"最可信 OCD App"（4.28/5）
- 与"锚"的定位最接近：碎片化、日常化

### 3. Perspectives（Mass General Brigham / 麻省总医院）
- 手机 CBT App，120 人 RCT：**65% 患者症状显著改善**
- 非专科教练（学士级）异步指导也有效
- 完整论文：PMC12753652

### 4. Liberate: My OCD Fighter
- 多个 OCD 资源网站推荐的自助 App

### 5. Wysa / Woebot（AI 聊天）
- CBT 基础对话机器人，Wysa 用户 150 万+，有 RCT 支持
- 非 OCD 专属，通用心理支持

### 6. OCD Challenge（ocdchallenge.com/zh）
- 互动式自定义治疗计划，**有中文版**，网页端可用

### 国内
- **PeacePoint**（App Store，中文界面）：针对重复检查循环
- **中国强迫症网站**（ocdcpa.cn）：科普 + CBT 自助指导
- 国内 tDCS 设备（英智科技等）存在，但**强迫症适应证证据不足**（上海交大医学院综述）

## 三、GitHub 开源项目（按路径）

### CBT/ERP 支持类
| 仓库 | 说明 | 值得借鉴 |
|---|---|---|
| `bchwangk/krishna` | OCD 知情 CBT/ERP 聊天机器人（Python CLI） | 状态机 + vignette 场景库结构 |
| `jsnicholas/OCDetour` | 延迟强迫行为 App（React 全栈） | 延迟计时交互 |
| `caldwellpatrickh/ocd-practice` | OCD 日常练习 + ERP 追踪（单文件 HTML） | 冥想脚本、SUDS、暴露阶梯 |
| `wondernoodle09/ocdapp` | ERP 疗法游戏化工具 | — |
| `pushpakcodes/MindEase` | 温和追踪 + AI 陪伴 | 追踪 UI |

### 记录类
- `spaciouskarter78/ERPMate`（Python）：ERP 会话记录，**焦虑时间曲线**（暴露后 5/10/30/60 分钟）

### VR 暴露
- `EishaRathore/CureOCD`（Dart/Flutter）：VR 暴露疗法

### 神经调控
- `Personalized-Neuromodulation/tDCS_ERP_OCD`（Python）：tDCS + ERP 研究

### 开源心理健康平台（架构参考）
- `BIDMCDigitalPsychiatry/LAMP-platform`（**mindLAMP**）：哈佛/贝斯以色列医院数字精神病学部门，开源数字表型平台
- `ChildMindInstitute/MindLogger`：儿童心理研究所的开源 applet 构建平台

> **结论**：GitHub 上 OCD 垂直开源项目普遍很小（★0–18），**没有成熟的中文开源生态**——这是「锚」的差异化机会。

## 四、对「锚」的启示（已落地）

| 借鉴来源 | 机制 | 在「锚」中的实现 |
|---|---|---|
| ocd.app | 每日微训练 | 每日 5 分钟微训练（v0.1） |
| OCDetour | 延迟强迫计时 | 念头停车场 + 担忧时间（v0.0.1） |
| ocd-practice | SUDS 量表 / 冥想脚本 / 暴露阶梯 / 冲动冲浪 | v0.1 全部落地 |
| krishna | 状态机对话 + vignette 结构 | AI 引导（v0.1） |
| ERPMate | 焦虑时间曲线 | 焦虑证据回访（v0.1） |
| mindLAMP | 数字表型思路 | 记录 → 触发模式分析（规划中） |

## 五、参考链接

- Mass General Brigham 临床试验：https://www.massgeneralbrigham.org/en/about/newsroom/press-releases/app-offers-treatment-for-obsessive-compulsive-disorder
- RCT 论文：https://pmc.ncbi.nlm.nih.gov/articles/PMC12753652/
- GGtude 科学背书：https://ggtude.com/the-science-behind-ggtude/
- ocd.app：https://ocd.app/
- mindLAMP：https://digitalpsych.org/mindlamp
