# Obsidian MCP Server

Claude가 Obsidian vault 파일에 직접 접근할 수 있게 해주는 MCP 서버입니다.

## 제공 기능

| Tool | 설명 |
|------|------|
| `list_notes` | vault 내 노트 목록 조회 (폴더 필터 지원) |
| `read_note` | 노트 내용 읽기 (frontmatter·태그·링크 파싱 포함) |
| `write_note` | 노트 생성 및 수정 |
| `search_notes` | 전체 텍스트 검색 |
| `list_tags` | 전체 태그 목록 및 사용 횟수 |
| `search_by_tag` | 특정 태그를 가진 노트 검색 |
| `get_backlinks` | 특정 노트를 링크하는 노트(백링크) 조회 |

---

## 설치

```bash
# 1. 의존성 설치
pip install mcp

# 또는 프로젝트 전체 설치
pip install -e .
```

---

## 설정

### Claude Desktop

설정 파일 위치:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

`claude_desktop_config.json`에 아래 내용을 추가하세요:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "python",
      "args": ["-m", "obsidian_mcp.server"],
      "cwd": "/path/to/obsidian-mcp",
      "env": {
        "OBSIDIAN_VAULT_PATH": "/your/obsidian/vault/path"
      }
    }
  }
}
```

> `OBSIDIAN_VAULT_PATH`를 실제 vault 경로로 변경하세요.

Claude Desktop을 재시작하면 적용됩니다.

---

### Claude Code (CLI)

프로젝트 루트 또는 홈 디렉토리의 `.claude/settings.json`에 추가:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "python",
      "args": ["-m", "obsidian_mcp.server"],
      "cwd": "/path/to/obsidian-mcp",
      "env": {
        "OBSIDIAN_VAULT_PATH": "/your/obsidian/vault/path"
      }
    }
  }
}
```

또는 CLI 명령어로 추가:

```bash
claude mcp add obsidian \
  --command python \
  --args "-m obsidian_mcp.server" \
  --env OBSIDIAN_VAULT_PATH=/your/vault/path
```

---

## 사용 예시

설정 완료 후 Claude에게 자연어로 요청할 수 있습니다:

```
vault에서 프로젝트 관련 노트 목록 보여줘
"머신러닝" 키워드로 노트 검색해줘
#todo 태그가 붙은 노트 목록 보여줘
"회의록/2024-01-15" 노트 내용 읽어줘
"아이디어/새프로젝트" 노트 만들어줘
"독서노트" 노트를 링크하는 노트 찾아줘
```

---

## 보안

- vault 외부 경로 접근은 차단됩니다 (path traversal 방지)
- `OBSIDIAN_VAULT_PATH`로 접근 범위를 vault로 제한합니다
