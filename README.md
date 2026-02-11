# OpenClaw Zhihu Auto Publisher

> 旧项目名：`zhihu`  
> 建议仓库新名称：`openclaw-zhihu-auto-publisher`

一个面向 OpenClaw 的知乎自动发布 Skills 项目：
- 自动选题（可选）
- 自动生成知乎长文
- 自动打开知乎写作页并发布

目标是让开发者在几分钟内完成复线，而不是读一堆分散文档。

## 这个项目解决什么问题

手动发布知乎文章通常要重复做这些事：
1. 想主题
2. 写大纲和正文
3. 打开知乎编辑器
4. 粘贴长文，处理格式错位
5. 点发布并确认结果

本仓库把以上流程打包成可复用 skills，并提供稳定脚本（CDP + 分批粘贴）降低发布失败率。

## 核心功能

- `zhihu-topic-ideator`：生成 1 个知乎选题（主题/角度/标题/要点）
- `zhihu-content-writer`：生成知乎纯文本长文
- `zhihu-social-publisher`：自动填充知乎编辑器并发布
- `zhihu-auto-publisher`：一条指令串起“选题 -> 写作 -> 发布”

## 1 分钟快速复线

### 1) 克隆项目

```bash
git clone https://github.com/liyxianren/zhihu.git
cd zhihu
```

### 2) 安装依赖

```bash
npm i -g agent-browser
```

### 3) 启动 Chrome（CDP）并登录知乎

```bash
bash skills/zhihu-social-publisher/scripts/start_zhihu_chrome.sh
```

首次必须在 Chrome 中手动完成知乎登录（扫码/验证码）。

### 4) 安装 skills 到 OpenClaw

```bash
cp -R skills/* ~/.openclaw/skills/
```

### 5) 在 OpenClaw 中直接触发

```text
帮我写一篇关于 2026 ISEF 选题策略的文章并发送到知乎
```

或：

```text
发送知乎
```

## 运行前置条件

- macOS 或 Linux
- OpenClaw 环境可用
- Google Chrome 已安装
- `agent-browser` 已安装并可执行
- 本机可用 CDP 端口 `9222`

## 网站操作插件说明（重点）

本项目依赖的网站自动化插件是：`agent-browser`。

它的作用：
- 通过 Chrome CDP 控制真实浏览器
- 在知乎编辑器中执行 click/fill/snapshot/screenshot 等动作

是否需要把插件放进本仓库？
- 不需要把 `agent-browser` 二进制或 node_modules 提交到仓库。
- 推荐做法：在使用机器上全局安装 `agent-browser`，仓库只保留封装脚本。
- 本仓库已提供封装脚本：
  - `skills/zhihu-social-publisher/scripts/ab_zhihu.sh`
  - `skills/zhihu-social-publisher/scripts/start_zhihu_chrome.sh`
  - `skills/zhihu-social-publisher/scripts/zhihu_paste_chunks.py`

这样仓库更轻、维护更简单、升级插件也更容易。

## 目录结构

```text
skills/
  zhihu-topic-ideator/
  zhihu-content-writer/
  zhihu-social-publisher/
    references/
      zhihu-workflow.md
    scripts/
      ab_zhihu.sh
      start_zhihu_chrome.sh
      zhihu_paste_chunks.py
  zhihu-auto-publisher/
```

## 设计约束

- 当前版本只支持知乎发布。
- 默认输出为知乎纯文本，不包含品牌引流和联系方式。

## 常见问题

1. `CDP endpoint is not reachable`
- 先执行 `bash skills/zhihu-social-publisher/scripts/start_zhihu_chrome.sh`
- 确认 Chrome 没被系统策略阻止调试端口

2. 已打开 Chrome 但提示 `No page found`
- 脚本会自动补开 tab；若仍失败，手动打开一个知乎页面后重试

3. 正文粘贴错位/漏段
- 调小 `--chunk-size`（如 400）
- 增大 `--wait-ms`（如 1000）

4. 点击发布后没有文章链接
- 知乎通常是二次确认弹窗，需完成最终确认按钮
- 以 `https://zhuanlan.zhihu.com/p/` 链接为发布成功标准

## 为什么开发者会愿意 Star

- 功能单一明确：只做知乎自动发布，不做泛平台噪音
- 复线门槛低：README 就能跑通
- 工程可维护：脚本封装、流程文档、失败判定都明确

如果你是来找“知乎自动发布 skills”的，这个仓库就是为这个场景做的。

## License

MIT
