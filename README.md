# Zhihu Skills Pack for OpenClaw

把“知乎内容生成 + 自动发布”相关的技能打包到一个仓库，方便他人一键复制到本地使用。

## 包含技能

- `skills/content-auto-publisher`
- `skills/content-writer`
- `skills/social-publisher`
- `skills/topic-ideator-scf`

其中自动发布知乎所需脚本与流程文档已包含在：

- `skills/social-publisher/references/zhihu-workflow.md`
- `skills/social-publisher/scripts/*`

## 安装方式

将本仓库的 `skills/` 下目录复制到你的 OpenClaw skills 目录：

```bash
# 示例（按你的环境调整）
cp -R skills/* ~/.openclaw/skills/
```

## 使用方式

在 OpenClaw 对话中可直接使用：

- `帮我写{主题}发送到知乎`
- `发送知乎`（自动选题 + 写作 + 发布）

## 注意事项

1. 该套流程以知乎发布为主；小红书在 `content-auto-publisher` 中标注为“内容可生成，发布暂未实现”。
2. `social-publisher` 发布链路依赖浏览器自动化环境，请先确认本地浏览器与登录状态可用。
3. 建议先阅读各技能 `SKILL.md`，理解约束与行为后再上线使用。

## 目录结构

```text
skills/
  content-auto-publisher/
  content-writer/
  social-publisher/
    references/
    scripts/
  topic-ideator-scf/
```
