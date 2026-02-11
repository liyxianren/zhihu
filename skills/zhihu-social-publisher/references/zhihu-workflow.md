# 知乎文章发布流程（稳定写入版）

使用 `agent-browser` 通过 CDP 连接 Google Chrome，在知乎专栏完成写入、预览与发布。

**不要直接调用 `agent-browser`。统一使用：**

```bash
bash {baseDir}/scripts/ab_zhihu.sh <command> [args...]
```

该脚本会自动加 `--cdp 9222`，并在 CDP 未就绪时直接报错，避免误开测试浏览器。

---

## Step 0: 启动 Chrome（调试模式）

如果 9222 端口未就绪，先启动 Chrome：

```bash
bash {baseDir}/scripts/start_zhihu_chrome.sh
```

说明：

- `--user-data-dir` 是登录态持久化的关键。
- 只要目录不删，知乎登录态通常会保留。
- 启动脚本会检查 CDP 是否存在可附着页面；若只有端口没有 tab，会自动补开页面。

---

## Step 1: 打开知乎写作页

```bash
bash {baseDir}/scripts/ab_zhihu.sh open "https://zhuanlan.zhihu.com/write"
bash {baseDir}/scripts/ab_zhihu.sh wait --load networkidle
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
```

---

## Step 2: 检查登录态

判断逻辑：

- 若出现“登录/扫码/验证码”等元素，视为未登录。
- 若出现编辑器工具栏、多个 `textbox`、`发布` 按钮，视为已登录。

未登录时：

```bash
bash {baseDir}/scripts/ab_zhihu.sh open "https://www.zhihu.com/signin"
```

提示用户在 Chrome 中手动登录，完成后回到写作页：

```bash
bash {baseDir}/scripts/ab_zhihu.sh open "https://zhuanlan.zhihu.com/write"
bash {baseDir}/scripts/ab_zhihu.sh wait --load networkidle
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
```

---

## Step 3: 获取标题 ref 与正文 ref（不要写死）

先列出当前 snapshot 中的 textbox 行：

```bash
python3 - <<'PY'
import json
obj=json.load(open('/tmp/zhihu-snapshot.json','r',encoding='utf-8'))
snap=obj.get('data',{}).get('snapshot','')
for ln in snap.splitlines():
    if 'textbox' in ln and 'ref=' in ln:
        print(ln)
PY
```

经验上：

- 第一个 textbox 常是标题
- 第二个 textbox 常是正文编辑区

但要以当前 snapshot 为准，不要硬编码成 `@e28`。

---

## Step 4: 填写标题

```bash
bash {baseDir}/scripts/ab_zhihu.sh fill @title_ref "2026康莱德竞赛：从选题到路演的实战指南"
bash {baseDir}/scripts/ab_zhihu.sh wait 800
```

---

## Step 5: 分批粘贴正文（推荐）

使用内置脚本进行稳定粘贴：

```bash
python3 {baseDir}/scripts/zhihu_paste_chunks.py \
  --file ~/clawd/publish-content.txt \
  --editor-ref @body_ref \
  --cdp 9222 \
  --session zhihu-cdp \
  --chunk-size 500 \
  --wait-ms 800
```

默认会在粘贴前做轻量归一化：

- 删除独立的 markdown 分隔线（如 `---`）
- 收敛过多空行为标准段落间距
- 清理常见不可见字符（如零宽字符、BOM）

如需保留原文逐字格式，添加参数 `--no-normalize`。

关键点：

- 每批都重新点击正文编辑区再粘贴
- 每批粘贴前会先把光标移动到正文末尾，避免长文出现段落错位（如 1-3-5-4-2）
- 使用系统原生剪贴板粘贴，不用 `eval` 注入正文
- 长文优先小批次（400-700）降低错乱概率
- 脚本内置命令超时与 CDP 存活检查；若浏览器崩溃会直接失败退出，不会无限运行

---

## Step 6: 写入校验（只读）

```bash
cat <<'JS' | bash {baseDir}/scripts/ab_zhihu.sh eval --stdin
(() => {
  const titleInput = document.querySelector('textarea[placeholder*="标题"], input[placeholder*="标题"], [contenteditable="true"][placeholder*="标题"]');
  const title = titleInput ? (titleInput.value || titleInput.textContent || '').trim() : '';
  const editables = Array.from(document.querySelectorAll('[contenteditable="true"]'));
  let best = '';
  for (const el of editables) {
    const t = (el.innerText || el.textContent || '').trim();
    if (t.length > best.length) best = t;
  }
  return { title, titleLen: title.length, bodyLen: best.length, bodyPreview: best.slice(0, 120) };
})();
JS
```

也可以通过包装脚本执行：

```bash
cat <<'JS' | bash {baseDir}/scripts/ab_zhihu.sh eval --stdin
(() => ({ ok: true }))();
JS
```

再做可视化截图：

```bash
bash {baseDir}/scripts/ab_zhihu.sh screenshot ~/Desktop/zhihu-preview.png --full
```

---

## Step 7: 上传图片（可选）

封面或文内图都遵循同一模式：

1. 先 `snapshot -i --json`
2. 找到上传按钮/输入控件 ref
3. 执行 `upload`
4. 等待并重新 snapshot 验证

示例：

```bash
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
bash {baseDir}/scripts/ab_zhihu.sh upload @upload_ref ~/path/to/image.png
bash {baseDir}/scripts/ab_zhihu.sh wait 5000
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
```

---

## Step 8: 发布前确认（必做）

向用户展示预览截图并确认：

- 标题是否正确
- 正文是否完整
- 图片是否正确
- 本次操作是“发布”还是“保存草稿”

未收到明确确认，不允许点发布。

---

## Step 9a: 发布文章

用户确认发布后：

```bash
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
bash {baseDir}/scripts/ab_zhihu.sh click @publish_ref
bash {baseDir}/scripts/ab_zhihu.sh wait 1500
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot-after-publish-click.json
```

这是两段式发布流程（必做）：

1. 第一次点击页面主按钮 `发布`（`@publish_ref`）。
2. 第二次处理弹窗中的最终确认按钮（常见文案：`确认`、`发布于 ...` 等）。

若出现发布设置弹窗（话题、专栏等），按当前 snapshot 完成必填项后点击最终确认按钮：

```bash
bash {baseDir}/scripts/ab_zhihu.sh click @confirm_ref
bash {baseDir}/scripts/ab_zhihu.sh wait 3000
```

发布后：

```bash
bash {baseDir}/scripts/ab_zhihu.sh screenshot ~/Desktop/zhihu-published.png
bash {baseDir}/scripts/ab_zhihu.sh get url
```

发布成功判定（必须同时满足）：

1. 已保存 `~/Desktop/zhihu-published.png`
2. `get url` 返回 `https://zhuanlan.zhihu.com/p/` 开头的文章 URL

---

## Step 9b: 保存草稿

```bash
bash {baseDir}/scripts/ab_zhihu.sh snapshot -i --json > /tmp/zhihu-snapshot.json
bash {baseDir}/scripts/ab_zhihu.sh click @draft_ref
bash {baseDir}/scripts/ab_zhihu.sh wait 2000
bash {baseDir}/scripts/ab_zhihu.sh screenshot ~/Desktop/zhihu-draft.png
```

---

## 异常处理

### 1) CDP 连接失败

```bash
bash {baseDir}/scripts/start_zhihu_chrome.sh
```

无响应则回到 Step 0。

### 2) 粘贴错乱/漏字

按顺序处理：

1. 重新 snapshot，确认正文 ref 仍有效
2. 降低 `--chunk-size`（例如 500）
3. 增加 `--wait-ms`（例如 1000）
4. 仅重贴失败段，不要整篇重来

### 3) 发布按钮不可点

- 检查标题是否为空
- 检查正文是否过短
- 检查弹窗是否有必填项

### 4) 验证码/安全验证

```bash
bash {baseDir}/scripts/ab_zhihu.sh screenshot ~/Desktop/zhihu-captcha.png
```

暂停并等待用户在 Chrome 窗口中手动完成验证。
