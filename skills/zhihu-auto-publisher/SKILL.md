---
name: zhihu-auto-publisher
description: End-to-end Zhihu auto flow: topic generation -> outline -> full article -> browser publishing from one command like “帮我写XX发送到知乎”.
metadata: {"openclaw":{"emoji":"⚙️","os":["darwin","linux"],"requires":{"bins":[]}}}
user-invocable: true
---

# Zhihu Auto Publisher

把“选题 + 写作 + 自动发布知乎”整合为一次流程。

## 强制依赖（执行前必须读取）
1. `zhihu-content-writer/SKILL.md`（写作规则）
2. `zhihu-social-publisher/SKILL.md`（发布流程）
3. `zhihu-topic-ideator/SKILL.md`（自动选题）

## 触发入口
- `帮我写{主题}发送到知乎`
- `发送知乎`
- `发布到知乎`

## 路由规则
凡是“发送/发布到知乎”类指令，优先进入本技能。

## 总流程（自动模式）
1. 解析用户主题。
2. 若未给主题，调用 `zhihu-topic-ideator` 生成 1 个主题卡片。
3. 生成大纲（自动模式下不等待用户确认）。
4. 按 `zhihu-content-writer` 规范生成全文。
5. 按 `zhihu-social-publisher` 规范自动发布。

## 约束
- 禁止输出品牌引流信息与联系方式。
- 禁止编造个人录取成绩等不可核实细节。
- 自动发布结束后必须返回：
  - 文章链接
  - 发布截图路径

## 输出
发布成功：
- status: published
- url: https://zhuanlan.zhihu.com/p/xxxxxx
- screenshot: ~/Desktop/zhihu-published.png

发布失败：
- status: failed
- reason: <失败原因>
- screenshot: <如有>
