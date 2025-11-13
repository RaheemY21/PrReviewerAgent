# PrReviewerAgent
You are an expert full-stack DevOps engineer and AI automation specialist. Build a complete, production-ready AI agent that does the following when given a public or private GitHub repository URL:

### GOAL
Create an autonomous AI agent that:
1. Clones the repo
2. Detects the language and dependency manager(s)
3. Identifies ALL outdated dependencies
4. Creates a new branch: `ai-deps-update-YYYY-MM-DD`
5. Updates dependencies to the latest **compatible** versions (respecting semver)
6. Runs the test suite (if any)
7. Creates a Pull Request with:
   - Summary table of updates
   - Security vulnerability highlights (if any)
   - Changelog links
   - Test status
   - AI-generated risk assessment

### REQUIREMENTS
- Support: **Node.js (npm/yarn/pnpm), Python (pip/requirements.txt/Pipfile/pyproject.toml), Java (Maven/Gradle), Go (go.mod), Ruby (Gemfile)**
- Use **GitHub API** (via PyGitHub or Octokit.js)
- Use **GitHub Actions** for CI/CD integration
- Use **LLM** (you) to:
  - Parse `package.json`, `requirements.txt`, etc.
  - Run `npm outdated`, `pip list --outdated`, etc.
  - Detect breaking changes via changelogs
  - Write safe commit messages
  - Generate PR body with Markdown table
- Handle **monorepos** (multiple dependency files)
- Skip updates that break tests (rollback or comment)
- Use **fine-grained GitHub tokens**
- Include **setup guide** (GitHub App, secrets, workflow YAML)

### OUTPUT
Return:
1. **Complete Python script** (`ai_dep_updater.py`) OR **Node.js version** — your choice
2. **GitHub Actions workflow YAML** to run it weekly
3. **Installation & setup instructions** (step-by-step)
4. **Example PR output** (what the bot posts)
5. **Security & error handling** (rate limits, auth, fallbacks)

Use best practices: logging, error handling, dry-run mode, config file.

Start with:  
"Here's your AI Dependency Update Agent — ready to deploy in 5 minutes:"
