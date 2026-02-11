---
name: zhihu-social-publisher
description: Publish user-provided title and body to Zhihu using OpenClaw + agent-browser (CDP). Use only when title+body are ready and user asks to publish.
homepage: https://github.com/liyxianren/zhihu
metadata: {"openclaw":{"emoji":"🚀","os":["darwin","linux"],"requires":{"bins":["agent-browser"]},"install":[{"id":"node","kind":"node","package":"agent-browser","bins":["agent-browser"],"label":"Install agent-browser (npm)"}]}}
user-invocable: true
---

# Zhihu Social Publisher

用 OpenClaw 调用 `agent-browser`，自动将内容发布到知乎专栏。

## 触发条件
- 用户已提供标题+正文，并明确要求“发布到知乎”。
- 如果用户只说“发送知乎/发知乎”但没提供完整内容，必须转到 `zhihu-auto-publisher`。

## 前置条件（必须满足）
1. 已安装 `agent-browser`。
2. 已安装 Google Chrome。
3. 已先打开 Chrome 并完成知乎登录（首次必须手动扫码/验证码）。
4. 本机可访问 CDP 端口 `9222`。

## 工作流程
确认内容 -> 打开知乎写作页 -> 检查登录态 -> 填标题 -> 分批粘贴正文 -> 截图预览 -> 用户确认 -> 发布 -> 返回链接

## 强约束
1. 不直接调用 `agent-browser`，统一用：
   `bash {baseDir}/scripts/ab_zhihu.sh ...`
2. 每次页面变化后必须重新 `snapshot`，禁止复用旧 ref。
3. 正文写入优先 `scripts/zhihu_paste_chunks.py`，禁止 `eval` 注入整篇正文。
4. 默认必须先截图并等待用户确认后再发布。
5. 发布成功需同时满足：
   - 保存发布后截图：`~/Desktop/zhihu-published.png`
   - `get url` 返回 `https://zhuanlan.zhihu.com/p/` 链接

自动发布特例：
- 若用户明确要求“全自动/无需确认”，可跳过预览确认直接发布。

## 快速命令
启动并检查 Chrome/CDP：
`bash {baseDir}/scripts/start_zhihu_chrome.sh`

打开写作页：
`bash {baseDir}/scripts/ab_zhihu.sh open "https://zhuanlan.zhihu.com/write"`

分批粘贴正文：
`python3 {baseDir}/scripts/zhihu_paste_chunks.py --file ~/clawd/publish-content.txt --editor-ref @body_ref --cdp 9222 --session zhihu-cdp --chunk-size 500 --wait-ms 800`

详细步骤见：`references/zhihu-workflow.md`
