"""
Obsidian MCP Server
Obsidian vault 파일에 Claude가 직접 접근할 수 있게 해주는 MCP 서버
"""

import os
import re
import json
from pathlib import Path
from typing import Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

VAULT_PATH = Path(os.environ.get("OBSIDIAN_VAULT_PATH", ""))

app = Server("obsidian-mcp")


def get_vault() -> Path:
    if not VAULT_PATH or not VAULT_PATH.is_dir():
        raise ValueError(
            f"유효하지 않은 vault 경로: '{VAULT_PATH}'. "
            "OBSIDIAN_VAULT_PATH 환경변수를 올바른 vault 경로로 설정하세요."
        )
    return VAULT_PATH


def resolve_note_path(vault: Path, note_path: str) -> Path:
    """노트 경로를 절대 경로로 변환하고 vault 내부인지 확인"""
    if not note_path.endswith(".md"):
        note_path = note_path + ".md"
    full_path = (vault / note_path).resolve()
    if not str(full_path).startswith(str(vault.resolve())):
        raise ValueError("vault 외부 경로는 접근할 수 없습니다.")
    return full_path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """YAML frontmatter와 본문을 분리"""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter_str = content[3:end].strip()
            body = content[end + 3:].strip()
            frontmatter = {}
            for line in frontmatter_str.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    frontmatter[key.strip()] = val.strip()
            return frontmatter, body
    return {}, content


def extract_tags(content: str, frontmatter: dict) -> list[str]:
    """frontmatter와 본문에서 태그 추출"""
    tags = set()

    # frontmatter tags
    raw_tags = frontmatter.get("tags", "")
    if raw_tags:
        for t in re.split(r"[,\s]+", raw_tags):
            t = t.strip().lstrip("#")
            if t:
                tags.add(t)

    # inline tags (#tag)
    for match in re.finditer(r"(?<!\w)#([\w/]+)", content):
        tags.add(match.group(1))

    return sorted(tags)


def extract_wikilinks(content: str) -> list[str]:
    """[[링크]] 형식의 wikilink 추출"""
    links = []
    for match in re.finditer(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", content):
        links.append(match.group(1).strip())
    return links


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_notes",
            description="vault 내 마크다운 노트 목록을 반환합니다. 선택적으로 하위 폴더를 지정할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "검색할 하위 폴더 경로 (기본값: vault 루트)",
                    }
                },
            },
        ),
        types.Tool(
            name="read_note",
            description="특정 노트의 내용을 읽습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "노트 경로 (vault 기준 상대 경로, .md 확장자 생략 가능)",
                    }
                },
                "required": ["path"],
            },
        ),
        types.Tool(
            name="write_note",
            description="노트를 생성하거나 덮어씁니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "노트 경로 (vault 기준 상대 경로)",
                    },
                    "content": {
                        "type": "string",
                        "description": "노트 내용 (마크다운)",
                    },
                },
                "required": ["path", "content"],
            },
        ),
        types.Tool(
            name="search_notes",
            description="노트 내용을 전체 텍스트 검색합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색어",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "대소문자 구분 여부 (기본값: false)",
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_tags",
            description="vault 전체에서 사용된 태그 목록과 각 태그가 사용된 노트 수를 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="search_by_tag",
            description="특정 태그가 있는 노트 목록을 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "검색할 태그 (# 기호 제외)",
                    }
                },
                "required": ["tag"],
            },
        ),
        types.Tool(
            name="get_backlinks",
            description="특정 노트를 링크하는 다른 노트(백링크) 목록을 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "백링크를 찾을 노트 경로",
                    }
                },
                "required": ["path"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    try:
        vault = get_vault()

        if name == "list_notes":
            folder = arguments.get("folder", "")
            base = (vault / folder).resolve() if folder else vault.resolve()
            if not str(base).startswith(str(vault.resolve())):
                raise ValueError("vault 외부 폴더는 접근할 수 없습니다.")

            notes = []
            for md_file in sorted(base.rglob("*.md")):
                rel = md_file.relative_to(vault)
                notes.append(str(rel))

            result = f"총 {len(notes)}개 노트\n\n" + "\n".join(notes)
            return [types.TextContent(type="text", text=result)]

        elif name == "read_note":
            note_path = resolve_note_path(vault, arguments["path"])
            if not note_path.exists():
                raise FileNotFoundError(f"노트를 찾을 수 없습니다: {arguments['path']}")

            content = note_path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(content)
            tags = extract_tags(content, frontmatter)
            links = extract_wikilinks(content)

            meta = []
            if frontmatter:
                meta.append(f"Frontmatter: {json.dumps(frontmatter, ensure_ascii=False)}")
            if tags:
                meta.append(f"Tags: {', '.join('#' + t for t in tags)}")
            if links:
                meta.append(f"Links: {', '.join('[[' + l + ']]' for l in links)}")

            output = content
            if meta:
                output = "---\n" + "\n".join(meta) + "\n---\n\n" + content

            return [types.TextContent(type="text", text=output)]

        elif name == "write_note":
            note_path = resolve_note_path(vault, arguments["path"])
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(arguments["content"], encoding="utf-8")
            action = "생성" if not note_path.exists() else "수정"
            return [types.TextContent(type="text", text=f"노트 {action} 완료: {arguments['path']}")]

        elif name == "search_notes":
            query = arguments["query"]
            case_sensitive = arguments.get("case_sensitive", False)
            flags = 0 if case_sensitive else re.IGNORECASE

            results = []
            for md_file in vault.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                matches = list(re.finditer(re.escape(query), content, flags))
                if matches:
                    rel = str(md_file.relative_to(vault))
                    snippets = []
                    for m in matches[:3]:
                        start = max(0, m.start() - 60)
                        end = min(len(content), m.end() + 60)
                        snippet = content[start:end].replace("\n", " ").strip()
                        snippets.append(f"  …{snippet}…")
                    results.append(
                        f"**{rel}** ({len(matches)}개 일치)\n" + "\n".join(snippets)
                    )

            if not results:
                return [types.TextContent(type="text", text=f"'{query}'에 대한 검색 결과 없음")]

            output = f"'{query}' 검색 결과 — {len(results)}개 노트\n\n" + "\n\n".join(results)
            return [types.TextContent(type="text", text=output)]

        elif name == "list_tags":
            tag_map: dict[str, list[str]] = {}
            for md_file in vault.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)
                tags = extract_tags(content, frontmatter)
                rel = str(md_file.relative_to(vault))
                for tag in tags:
                    tag_map.setdefault(tag, []).append(rel)

            if not tag_map:
                return [types.TextContent(type="text", text="태그 없음")]

            lines = [
                f"#{tag} ({len(notes)}개 노트)"
                for tag, notes in sorted(tag_map.items())
            ]
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "search_by_tag":
            target = arguments["tag"].lstrip("#")
            results = []
            for md_file in vault.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)
                tags = extract_tags(content, frontmatter)
                if target in tags:
                    results.append(str(md_file.relative_to(vault)))

            if not results:
                return [types.TextContent(type="text", text=f"#{target} 태그를 가진 노트 없음")]

            output = f"#{target} 태그 노트 {len(results)}개\n\n" + "\n".join(results)
            return [types.TextContent(type="text", text=output)]

        elif name == "get_backlinks":
            target_raw = arguments["path"].removesuffix(".md")
            target_names = {
                target_raw,
                Path(target_raw).name,
            }

            results = []
            for md_file in vault.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                links = extract_wikilinks(content)
                if any(l == name or l == Path(name).name for l in links for name in target_names):
                    results.append(str(md_file.relative_to(vault)))

            if not results:
                return [types.TextContent(type="text", text=f"'{arguments['path']}'를 링크하는 노트 없음")]

            output = f"백링크 {len(results)}개\n\n" + "\n".join(results)
            return [types.TextContent(type="text", text=output)]

        else:
            raise ValueError(f"알 수 없는 tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"오류: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
