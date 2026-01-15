# CLAUDE.md - AI Assistant Guide

**Last Updated:** 2026-01-15
**Repository Status:** Newly initialized, empty repository

---

## Repository Overview

### Current State
- **Location:** `/home/user/test`
- **Git Status:** Initialized git repository
- **Branch Strategy:** Feature branches prefixed with `claude/`
- **Content:** Repository is currently empty and awaiting initial project setup

### Project Purpose
*To be determined - this repository is ready for initial development*

---

## Codebase Structure

### Current Directory Layout
```
/home/user/test/
├── .git/              # Git version control metadata
└── CLAUDE.md          # This file
```

### Expected Structure (To Be Established)
As the project develops, document the directory structure here. Common patterns include:

```
/home/user/test/
├── src/               # Source code
├── test/              # Test files
├── docs/              # Documentation
├── config/            # Configuration files
├── scripts/           # Utility scripts
├── .github/           # GitHub workflows and templates
├── .gitignore         # Git ignore patterns
├── README.md          # Project documentation
└── CLAUDE.md          # This file
```

---

## Development Workflows

### Git Workflow

#### Branch Management
- **Feature Branches:** All development happens on feature branches
- **Naming Convention:** `claude/claude-md-<session-id>`
- **Current Branch:** `claude/claude-md-mkf1yyw2elaihnpy-T0Dkv`
- **Main Branch:** To be determined when established

#### Committing Changes
1. **Stage Changes:** Use `git add <files>` to stage relevant files
2. **Commit Message Format:**
   - Use clear, descriptive messages
   - Focus on the "why" rather than the "what"
   - Format: `<type>: <description>`
   - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
3. **Example:** `feat: add user authentication module`

#### Pushing Changes
- **Command:** `git push -u origin <branch-name>`
- **Critical:** Branch names must start with `claude/` and match session ID
- **Retry Logic:** On network failures, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

#### Pull Requests
When creating PRs:
1. Analyze all commits in the branch (not just the latest)
2. Include a comprehensive summary with:
   - **Summary:** 1-3 bullet points explaining changes
   - **Test Plan:** Checklist of testing steps
3. Use `gh pr create` command with HEREDOC format

### Code Safety & Security
- **Never** introduce security vulnerabilities:
  - Command injection
  - XSS (Cross-Site Scripting)
  - SQL injection
  - OWASP Top 10 vulnerabilities
- **Always** validate user input at system boundaries
- **Trust** internal code and framework guarantees
- **Fix** insecure code immediately upon detection

### Development Principles

#### Avoid Over-Engineering
- Make only changes that are directly requested or clearly necessary
- Keep solutions simple and focused
- Don't add unrequested features or "improvements"
- Don't add error handling for scenarios that can't happen
- Don't create abstractions for one-time operations
- Don't design for hypothetical future requirements

#### Code Changes
- **Read First:** Always read existing code before modifying
- **Minimal Changes:** Only modify what's necessary
- **No Premature Optimization:** Three similar lines are better than a premature abstraction
- **Delete Unused Code:** No backwards-compatibility hacks for unused code
- **No Unnecessary Comments:** Only comment where logic isn't self-evident

---

## Key Conventions

### File Operations
- **Read files:** Use `Read` tool (not `cat`)
- **Edit files:** Use `Edit` tool (not `sed/awk`)
- **Write files:** Use `Write` tool (not `echo >` or heredoc)
- **Search files:** Use `Grep` tool (not `grep` or `rg` commands)
- **Find files:** Use `Glob` tool (not `find` or `ls`)

### Tool Usage
- **Parallel Operations:** When tasks are independent, use parallel tool calls
- **Sequential Operations:** Use `&&` to chain dependent commands
- **Specialized Tools:** Prefer specialized tools over bash commands
- **Task Management:** Use `TodoWrite` to track multi-step tasks

### Code References
When referencing code, use the format: `file_path:line_number`

Example: "Error handling occurs in `src/services/process.ts:712`"

---

## Task Management

### Using TodoWrite
- **When to Use:**
  - Complex multi-step tasks (3+ steps)
  - Non-trivial and complex tasks
  - Multiple tasks from user
  - After receiving new instructions

- **When NOT to Use:**
  - Single, straightforward tasks
  - Trivial tasks with <3 steps
  - Purely conversational queries

### Task States
- `pending` - Not yet started
- `in_progress` - Currently working (limit to ONE at a time)
- `completed` - Finished successfully

### Task Format
Each task needs two forms:
- **content:** Imperative form ("Run tests", "Fix bug")
- **activeForm:** Present continuous form ("Running tests", "Fixing bug")

### Completion Rules
Only mark tasks as completed when:
- Fully accomplished
- No errors or blockers
- Tests passing (if applicable)
- Implementation is complete

---

## Testing & Quality

### Testing Practices
*To be established based on project type*

Common patterns:
- Run tests before committing
- Fix all failing tests
- Maintain test coverage
- Add tests for new features

### Code Quality
- Follow project linting rules
- Maintain consistent code style
- Write self-documenting code
- Keep functions focused and small

---

## Communication Guidelines

### With Users
- Be concise and clear
- Use GitHub-flavored Markdown
- Output text directly (never use `echo` for communication)
- Avoid emojis unless requested
- No unnecessary superlatives or excessive praise

### Code Comments
- Only add comments where logic isn't self-evident
- Don't comment unchanged code
- Focus on "why" not "what"
- Keep comments up-to-date with code changes

---

## Project-Specific Notes

### Technology Stack
*To be documented when project technology is chosen*

### Build & Deployment
*To be documented when build system is established*

### Environment Setup
*To be documented when dependencies are added*

### Testing Commands
*To be documented when test framework is chosen*

---

## Common Patterns & Idioms

*This section should be updated as the codebase develops with:*
- Naming conventions
- Architectural patterns
- Common utilities and helpers
- Error handling patterns
- Logging conventions
- API design patterns

---

## Resources & References

### Documentation
- Repository README: *To be created*
- API Documentation: *To be created*
- Contributing Guidelines: *To be created*

### External Resources
- Git Best Practices: https://git-scm.com/book/en/v2
- Conventional Commits: https://www.conventionalcommits.org/

---

## Maintenance

### Updating This Document
This document should be updated when:
- Project structure changes significantly
- New conventions are established
- Development workflows are modified
- New tools or frameworks are added
- Architectural decisions are made

### Version History
- **2026-01-15:** Initial creation for empty repository

---

## Quick Reference

### Essential Commands
```bash
# Git operations
git status                              # Check repository status
git add <files>                         # Stage files
git commit -m "message"                 # Commit changes
git push -u origin <branch>             # Push to remote

# Branch operations
git checkout -b <branch-name>           # Create new branch
git branch                              # List branches
git log --oneline                       # View commit history
```

### AI Assistant Checklist
Before making changes:
- [ ] Read existing code first
- [ ] Understand the context
- [ ] Plan multi-step tasks with TodoWrite
- [ ] Ask clarifying questions if needed

During implementation:
- [ ] Make minimal, focused changes
- [ ] Avoid over-engineering
- [ ] Check for security vulnerabilities
- [ ] Update todos as you progress

Before committing:
- [ ] Run tests (when available)
- [ ] Review all changes
- [ ] Write clear commit messages
- [ ] Verify no sensitive data is included

---

*This document is a living guide. Keep it updated as the project evolves.*
