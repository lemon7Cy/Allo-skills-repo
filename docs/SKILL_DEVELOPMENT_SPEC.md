# Allo Skill 开发规范与约定

本文档定义 Allo Skills 仓库中 skill 的开发规范、安全约定和提交标准。

## 目录结构

```
plugins/
  <skill-name>/
    skills/
      <skill-name>/
        SKILL.md              ← 必须，skill 主文件
        references/           ← 可选，参考文档
        assets/               ← 可选，模板/图片等资源
        scripts/              ← 可选，辅助脚本
        setup.sh              ← 可选，首次安装脚本
        .env.example          ← 可选，环境变量模板
        requirements.txt      ← 可选，Python 依赖
```

## 1. SKILL.md Frontmatter 规范

每个 `SKILL.md` 必须包含 YAML frontmatter：

```yaml
---
name: skill-name                # 必须，小写连字符
description: 简短描述            # 必须
tools: []                       # 必须
version: "1.0.0"               # 推荐
author: allo-official           # 推荐
required_env:                   # 必须配置的凭据 key
  - API_TOKEN
optional_env:                   # 可选配置的凭据 key
  - OPTIONAL_KEY
credentials:                    # 凭据 UI 元数据
  - key: API_TOKEN
    label: 显示名称
    description: 用途说明
    required: true
    secret: true
---
```

### 字段说明

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | skill 名称，小写连字符，安装后保持稳定 |
| `description` | string | ✅ | 简短描述 |
| `tools` | array | ✅ | 通常为 `[]` |
| `version` | string | 推荐 | 版本号 |
| `author` | string | 推荐 | 作者 |
| `required_env` | string[] | 按需 | 必须配置的凭据 key 列表 |
| `optional_env` | string[] | 按需 | 可选凭据 key 列表 |
| `credentials` | object[] | 按需 | 凭据的 UI 元数据 |

### credentials 子字段

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `key` | string | ✅ | 凭据 key，大写 env 风格 |
| `label` | string | 推荐 | 人类可读标签 |
| `description` | string | 推荐 | 帮助文本 |
| `required` | boolean | 推荐 | 是否必须，默认 `true` |
| `secret` | boolean | 推荐 | 是否敏感，默认 `true` |
| `docs_url` | string | 可选 | 文档/token 创建页面 URL |

## 2. marketplace.json 规范

`marketplace.json` 中每个 skill 条目应与 `SKILL.md` frontmatter 保持一致：

```json
{
  "name": "skill-name",
  "source": "./plugins/skill-name",
  "description": "简短描述",
  "version": "1.0.0",
  "category": "research",
  "tags": ["tag1", "tag2"],
  "required_env": ["API_TOKEN"],
  "optional_env": [],
  "credentials": [
    {
      "key": "API_TOKEN",
      "label": "显示名称",
      "description": "用途说明",
      "required": true,
      "secret": true
    }
  ]
}
```

### category 值

| 值 | 说明 |
|------|------|
| `research` | 知识库查询、文献检索 |
| `presentation` | PPT、演示稿生成 |
| `productivity` | PDF 转换、数据处理 |
| `coding` | 代码相关 |
| `writing` | 写作相关 |
| `analysis` | 数据分析 |

## 3. 凭据命名规则

### 推荐命名

```
MINGXUE_API_TOKEN          ← 明学知识库
DONGFANG_API_TOKEN         ← 东方电子知识库
PDF_PARSE_TOKEN            ← PDF 解析 API
GPT_IMAGE_API_KEY          ← GPT 图片生成
```

### 禁止命名

```
API_KEY                    ← 太通用
TOKEN                      ← 太通用
SECRET                     ← 太通用
AUTH_TOKEN                 ← 太通用
```

规则：
- 大写 env 风格，下划线分隔
- 包含服务/功能前缀
- 以 `_TOKEN` 或 `_KEY` 结尾

## 4. 安全约定

### ✅ 允许

```bash
# 在 SKILL.md 正文中使用环境变量
curl -sS -X POST "http://example.com/api/search" \
  -H "Authorization: Bearer $MINGXUE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "SOC SOH RUL", "top_k": 5}'

# 也允许 ${VAR} 格式
curl -H "Authorization: Bearer ${MINGXUE_API_TOKEN}" ...
```

### 🚫 禁止

```bash
# 不要打印 token
echo $MINGXUE_API_TOKEN

# 不要开启调试模式
set -x

# 不要输出详细请求头（会泄露 token）
curl -v ...

# 不要把 token 放在 URL 参数里
https://api.example.com/search?token=$TOKEN

# 不要在代码中硬编码 token
TOKEN = "sk-xxxx..."

# 不要提交含 token 的文件到 git
# .env 文件必须在 .gitignore 中
```

### Token 传递方式

**必须用 Header**：
```bash
-H "Authorization: Bearer $TOKEN"
```

**禁止用 URL 参数**：
```bash
# 🚫 不要这样写
https://api.example.com?token=$TOKEN
```

## 5. API 地址约定

固定的服务地址可以硬编码到 SKILL.md 中（不是敏感信息）：

```yaml
# ✅ 允许硬编码 URL
Search API: http://221.0.79.251:18091/api/search
```

Token 必须通过环境变量传入：

```yaml
# ✅ Token 用环境变量
export MINGXUE_API_TOKEN="<your-token>"
```

## 6. Allo Desktop 凭据状态

Allo Desktop 通过 `settings.json` 管理凭据，自动检查状态：

| 状态 | 条件 |
|------|------|
| `not_configurable` | skill 未声明任何 key |
| `missing_required_credentials` | 有 required key 未配置 |
| `missing_optional_credentials` | required 已配，optional 未配 |
| `ready` | 所有声明的 key 已配置 |

凭据存储格式：
```json
{
  "credentials": {
    "skills": {
      "skill-name": {
        "API_TOKEN": "..."
      }
    }
  }
}
```

## 7. 提交检查清单

提交新 skill 或修改时，确认：

- [ ] `marketplace.json` 条目有稳定的 `name` 和有效的 `source`
- [ ] `SKILL.md` frontmatter 的 `name` 和 `description` 与 marketplace 一致
- [ ] 必须配置的 key 列在 `required_env`
- [ ] 可选配置的 key 列在 `optional_env`
- [ ] 每个 key 有 `credentials[]` 条目
- [ ] 没有只在正文中提到而未声明的凭据
- [ ] 正文中的 curl 示例用 `$KEY` 环境变量，不是硬编码值
- [ ] 没有 `echo $TOKEN`、`set -x`、`curl -v` 等泄露风险
- [ ] 没有 `?token=$KEY` 的 URL 参数传递方式
- [ ] `.env` 文件不在 git 中（在 `.gitignore`）
- [ ] skill 目录包含所有需要的 references/scripts/assets

## 8. 测试要求

每个 skill 应在 `tests/` 目录下有对应测试：

```python
class TestSkillName(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue(os.path.exists(SKILL_PATH))

    def test_skill_md_has_frontmatter(self):
        with open(SKILL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"))
        self.assertIn("name: skill-name", content)

    def test_skill_registered_in_marketplace(self):
        marketplace_path = os.path.join(REPO_ROOT, "marketplace.json")
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
        plugin_names = {p["name"] for p in marketplace["plugins"]}
        self.assertIn("skill-name", plugin_names)
```

运行测试：
```bash
python3 -m unittest tests.test_xxx -v
python3 scripts/validate_marketplace.py
```
