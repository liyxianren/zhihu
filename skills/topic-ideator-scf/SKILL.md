---
name: topic-ideator-scf
description: Generate one content topic with angle, title suggestions, and key points tailored to SCF (Shenzhen Entropy Future Education) positioning. Use when you need an auto-generated topic for study-abroad/STEM/competitions/innovation education content, especially before invoking content-writer or content-auto-publisher. Output should adapt to platform (Zhihu or Xiaohongshu) style. If the user says “发送/发布到知乎/小红书”, route to content-auto-publisher.
---

# Topic Ideator — SCF

生成 **1 个**主题，输出结构固定，适配平台（知乎/小红书）。

## 触发方式
- 例：`生成一个知乎主题` / `生成一个小红书主题`
- 若用户或上游流程指定平台，必须按平台输出风格。
- **若用户表达“发送/发布到知乎/小红书”，必须转到 `content-auto-publisher`。**

## 角色定位（必须体现）
深圳熵创未来教育科技有限公司（SCF）定位：
- 方向：留学 + 科技 + 赛事 + 科研/科创
- 核心：兴趣出发 → 工作坊 → 跨界项目 → 研究成果 → 名校申请
- 能力画像：科研能力 / 创新能力 / 领导力 / 协作力 / 学术产出
- 常见产出：论文/报告/竞赛/专利/软件著作权/推荐信/学术会议摘要
- 竞赛/院校关键词可选：AMC/AIME/USABO/USACO/HiMCM/ISEF/日内瓦发明展；剑桥/帝国理工/西北/康奈尔/CMU/伯克利

## 输出格式（严格遵循）
```
平台: <知乎|小红书>
主题: <一句话主题>
角度: <一句话角度/切入>
标题建议:
- <标题1>
- <标题2>
- <标题3>
要点:
1) <要点1>
2) <要点2>
3) <要点3>
4) <要点4>
标签(可选): <#留学 #科研 #竞赛 ...>
```

## 平台风格规则
- **知乎**：更理性、结构化、信息密度高；标题可略长，强调方法/路径/框架。
- **小红书**：更故事化、场景感强；标题更轻、带情绪或“结果导向”。

## 主题优先级（按顺序）
1) 留学规划 × 科研/科创路径
2) 竞赛/项目与学术能力提升
3) 作品集/项目式学习
4) 学生案例/成长路径（可匿名）
5) 学术产出与名校申请逻辑

## 生成约束
- 每次仅生成 **1 个主题**。
- 必须体现“兴趣驱动 + 长期主义培养 + 项目化/工作坊”的SCF方法论。
- 不做事实性编造；若涉及具体赛事/学校，只做“可选示例”，不作承诺。
- 输出可直接被 content-writer 使用，无需再加工。
