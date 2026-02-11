---
name: zhihu-content-writer
description: Write long-form Zhihu posts in pure text for study-abroad/STEM/competition/research/application topics. Use when the user asks to write Zhihu content. If the user says “发送/发布到知乎”, route to zhihu-auto-publisher.
homepage: https://github.com/liyxianren/zhihu
metadata: {"openclaw":{"emoji":"✍️","os":["darwin","linux","windows"],"requires":{"bins":[]}}}
user-invocable: true
---

# Zhihu Content Writer

只负责“知乎正文写作”，不执行发布。

## 工作流程（默认）
选题 -> 出大纲 -> 用户确认 -> 生成全文

## 路由规则
- 用户说“发送/发布到知乎”时，转到 `zhihu-auto-publisher`。
- 本技能只写作，不负责浏览器发布。

## 强约束
1. 先确认主题，再动笔。
2. 先给大纲，等用户确认后再写全文。
3. 不输出 Markdown，统一输出知乎可粘贴的纯文本。
4. 不出现机构品牌、联系方式、引流 CTA。

自动发布特例：
- 若上游是 `zhihu-auto-publisher`（用户明确要求全自动），可跳过大纲确认，直接生成全文。

## Step 1: 选题
用户未给主题时，给出简短菜单：
1. 竞赛规划（AMC/AIME/USABO/USACO/HiMCM/ISEF 等）
2. 科研项目（课题、方法、产出）
3. 作品集建设（项目结构与证据链）
4. 申请策略（时间线、选校、文书主线）
5. 家长与学生协同（资源配置与常见误区）
6. 自定义主题

## Step 2: 大纲格式（必须先给）
标题: <问题式或观点式>
引言: <背景与核心问题>
正文结构:
一、<现状或问题拆解>
二、<方法或框架>
三、<案例或执行细节>
结论: <总结与行动建议>

## Step 3: 全文写作规范（知乎）
- 输出格式：纯文本。
- 推荐字数：1800-3200 字。
- 标题长度：15-30 字。
- 必须包含：
  - 1 个趋势判断
  - 1 个时间线/流程框架
  - 1 个决策模型（取舍逻辑）
  - 至少 2 个具体案例或场景化示例
- 内容目标：可执行、可复用、可评估。

## 质量自检
- 标题与正文一致，不做标题党。
- 结构清晰：问题 -> 分析 -> 方法 -> 落地。
- 论点有依据，建议有步骤。
- 无夸大承诺、无品牌暴露、无联系方式。
- 可直接复制到知乎编辑器发布。
