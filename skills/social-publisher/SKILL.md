---
name: social-publisher
description: Publish user-provided content to social media platforms (Zhihu, Xiaohongshu) using agent-browser. Use only when the user explicitly provides正文/标题并要求发布（发布推文、发布文章、publish a post）。If the user says just “发送知乎/发知乎/发送小红书/发小红书” or only provides a topic or platform, route to content-auto-publisher instead.
homepage: https://github.com/limou/social-publisher-skill
metadata: {"openclaw":{"emoji":"🚀","os":["darwin","linux"],"requires":{"bins":["agent-browser"]},"install":[{"id":"node","kind":"node","package":"agent-browser","bins":["agent-browser"],"label":"Install agent-browser (npm)"}]}}
user-invocable: true
---

# Social Publisher

使用 `agent-browser` CLI 自动化发布内容到社交平台（知乎、小红书等）。

默认目标是先稳定完成“写入与预览”，再执行发布。

## 工作流程（默认）

```text
确认内容 -> 打开写作页 -> 检查登录态 -> 填标题 -> 分批粘贴正文 -> 截图预览 -> 用户确认 -> 发布/草稿
```

## 强约束

0. **触发路由规则：** 若用户仅说“发送知乎/发知乎/发送小红书/发小红书”或只给平台/主题（未提供标题+正文），必须转到 `content-auto-publisher`；**禁止**在本技能内继续发布。
1. 不直接调用 `agent-browser`。统一通过 `bash {baseDir}/scripts/ab_zhihu.sh ...` 调用（脚本会强制加 `--cdp 9222` 和独立 `--session zhihu-cdp`）。
2. 每次页面变化后必须重新 `snapshot`，不能复用旧 ref。
3. 禁止写死 ref（如 `@e28`）；ref 只在当前 snapshot 有效。
4. 正文写入优先用“分批原生粘贴”，不要用 `eval`/`execCommand` 注入正文。
5. 点击发布前必须截图并等待用户明确确认。
6. 发布成功必须同时满足：已保存发布后截图（`~/Desktop/zhihu-published.png`）且 `get url` 返回 `https://zhuanlan.zhihu.com/p/` 文章链接。

**自动发布特例（用户明确要求全自动时适用）：**
- 若用户明确要求“无需确认/全自动发布/自动发布”，允许跳过预览确认，直接点击发布。
- 仍需保存发布后截图并获取文章链接。

## 前置条件

- `agent-browser` 可用：`agent-browser --version`
- Google Chrome 可用
- 首次使用需要用户手动登录知乎

## CDP 登录态说明（重要）

此技能默认通过 Chrome 的 `--user-data-dir` 保持登录态。

- 推荐：固定 `--user-data-dir="/tmp/zhihu-chrome-profile"`
- 只要不删除该目录，登录态会保留
- 在 `--cdp` 场景下，不依赖 `--state` 作为主要恢复方案

## 推荐写入命令

先启动 Chrome（如未就绪）：

```bash
bash {baseDir}/scripts/start_zhihu_chrome.sh
```

该脚本会同时检查 CDP 端口和“是否有已附着页面”；若仅端口存活但无 tab，会自动补开页面，避免 `No page found`。

然后打开写作页并获取 refs：

```bash
bash {baseDir}/scripts/ab_zhihu.sh open "https://zhuanlan.zhihu.com/write"
bash {baseDir}/scripts/ab_zhihu.sh wait --load networkidle
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
```

根据 snapshot 选择标题 ref 与正文 ref 后：

```bash
bash {baseDir}/scripts/ab_zhihu.sh fill @title_ref "文章标题"
python3 {baseDir}/scripts/zhihu_paste_chunks.py \
  --file ~/clawd/publish-content.txt \
  --editor-ref @body_ref \
  --cdp 9222 \
  --session zhihu-cdp \
  --chunk-size 500 \
  --wait-ms 800
```

默认会做正文归一化（移除独立 `---` 分隔线、收敛异常空行、清理不可见字符）。如需保留原始格式，可追加 `--no-normalize`。

写入后验证与截图：

```bash
bash {baseDir}/scripts/ab_zhihu.sh wait 1500
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json
bash {baseDir}/scripts/ab_zhihu.sh screenshot ~/Desktop/zhihu-preview.png --full
```

## 平台流程文档

- 知乎：`references/zhihu-workflow.md`
- 小红书：后续补充

## 限制与异常

- 知乎 UI 变化会导致 ref 匹配变化，需要重新 snapshot
- 验证码必须用户手动处理
- 图片上传失败时先等待并重试一次，不做无限重试
- 分批粘贴期间不要手动点击编辑器或滚动页面，避免光标位置被人为打断

## Notes

- 始终使用 `agent-browser`，不要切到 Playwright/Puppeteer 脚本。
- 发布前必须让用户确认预览图。
- 若只看到发布设置/确认弹窗但未拿到文章 URL，不算发布完成，必须继续完成确认并复核 URL。
