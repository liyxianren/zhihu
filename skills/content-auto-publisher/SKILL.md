---
name: content-auto-publisher
description: End-to-end generate and auto-publish Zhihu/Xiaohongshu posts from a single command like “帮我写{主题}发送到知乎/小红书”. Use when the user wants a fully automatic write+publish flow without intermediate confirmations.
---

# Content Auto Publisher

将“写作 + 自动发布”合并为一次性流程。目标：用户一句话触发 → 自动写大纲 → 自动写全文 → 自动发布。

## 强制依赖（必须阅读）
在执行本技能前，**必须先读取以下技能文件并遵循其规则**：
1. `content-writer` 的 SKILL.md（写作风格、结构、字数、标签等）
2. `social-publisher` 的 SKILL.md（发布流程、约束、截图/链接要求）
3. `topic-ideator-scf` 的 SKILL.md（主题生成：主题/角度/标题/要点）

> 注意：不得仅凭“沿用”描述跳过读取。必须先读取，再执行。

## 触发指令（总入口）

- 形式A：**内容 + 平台（用户指定主题）**
  - 例：`帮我写2026康莱德发送到知乎`
  - 例：`写一篇康莱德比赛经验发布到小红书`
- 形式B：**仅平台（自动生成主题）**
  - 例：`发送知乎`
  - 例：`发小红书`

**路由规则（强制）：**凡是“发送/发布到知乎/小红书”的指令，必须优先进入本技能作为总流程入口。

## 总流程（自动模式）

0) **先读取** content-writer / social-publisher / topic-ideator-scf 的 SKILL.md（强制）
1) 解析平台
2) 若用户未给出明确主题：调用 `topic-ideator-scf` 生成「主题+角度+标题+要点」
3) 生成大纲（不要求用户确认）
4) 生成全文（**严格遵循 content-writer 的全部风格/结构/字数/标签规则**）
5) 自动发布（**严格遵循 social-publisher 的流程与强约束**）

## 强制约束

- **禁止使用 web_search**。如需事实校验或引用，以用户提供信息为准，或明确标注为一般性经验判断。

> 说明：该技能处于“全自动模式”，不会请求用户确认。

## 写作要求（沿用 content-writer）

- 平台格式、语气、字数、标签等规则完全沿用 `content-writer`。
- 自动模式下允许跳过“大纲确认”。
- 若主题为知乎，可直接进入生成全文。
- 若主题来自 `topic-ideator-scf`，需将其「角度/要点/标题」作为写作约束与结构依据。

## 发布要求（沿用 social-publisher）

- 发布环节必须遵循 `social-publisher` 中对知乎发布的流程与脚本约束。
- 触发自动发布时，允许跳过预览确认，直接发布。

## 平台处理

### 知乎
- 生成知乎格式全文（纯文本）
- 调用 social-publisher 的知乎发布流程自动发布

### 小红书（暂未实现发布）
- 生成小红书版本正文（Markdown）
- **不执行发布**：保存内容并明确提示“小红书发布接口未实现，已生成内容待发布”

## 输出要求

- 自动发布后需返回发布结果（知乎文章链接 + 发布截图路径）
- 小红书未发布时，返回生成内容与提示信息
