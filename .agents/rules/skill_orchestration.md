# Skill Orchestration Protocol for ArtisanConnect

## Priority 1: Workspace Skills
The primary engineering skills for this project are scoped in `.agents/skills/`.
They must always be prioritized and consulted before writing code, modifying architecture, reviewing security, or running tests:
- `django-patterns`, `django-security`, `django-tdd`
- `python-patterns`, `python-testing`
- `postgres-patterns`, `api-design`
- `frontend-ui-engineering`, `design-taste-frontend`, `make-interfaces-feel-better`, `web-accessibility-a11y`
- `code-review-and-quality`, `code-simplification`, `performance-optimization`, `test-driven-development`

## Priority 2: Full 500-Skill Repository Access
Whenever a request involves a domain or technology outside the workspace core (e.g., Docker, Kubernetes, Nginx, Redis, WebSockets, Mobile, CI/CD pipelines, Machine Learning, Reverse Engineering):
1. Do not assume the skill is unavailable because of prompt budget truncation.
2. Execute `python scripts/skill_finder.py <keyword>` to locate the skill on disk instantly.
3. Read its full `SKILL.md` via `read_file` before starting the task.
4. Announce the selected skill at the beginning of the response.
