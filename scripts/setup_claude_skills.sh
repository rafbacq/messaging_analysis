#!/usr/bin/env bash
set -euo pipefail

# Sets up repo-local Claude Code skills for:
# - ML research engineering
# - MLOps / production ML
# - token discipline
# - code quality
# - private text-data safety
#
# Run from your repo root:
#   bash scripts/setup_claude_skills.sh

PROJECT_ROOT="$(pwd)"
SKILLS_DIR="$PROJECT_ROOT/.claude/skills"
CACHE_DIR="${CLAUDE_SKILL_CACHE:-$HOME/.cache/claude-skill-repos}"

mkdir -p "$SKILLS_DIR"
mkdir -p "$CACHE_DIR"

log() {
  printf "\n[setup-claude-skills] %s\n" "$1"
}

clone_or_update() {
  local repo_url="$1"
  local dest="$2"

  if [ -d "$dest/.git" ]; then
    log "Updating $(basename "$dest")"
    git -C "$dest" pull --ff-only || true
  else
    log "Cloning $repo_url"
    rm -rf "$dest"
    git clone --depth 1 "$repo_url" "$dest"
  fi
}

copy_dir() {
  local src="$1"
  local dest="$2"

  rm -rf "$dest"
  mkdir -p "$dest"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$src/" "$dest/"
  else
    (
      cd "$src"
      tar cf - .
    ) | (
      cd "$dest"
      tar xf -
    )
  fi
}

find_skill_file() {
  local repo="$1"
  local skill_name="$2"

  find "$repo" -type f -name SKILL.md 2>/dev/null | while IFS= read -r file; do
    local folder_name
    folder_name="$(basename "$(dirname "$file")")"

    if [ "$folder_name" = "$skill_name" ]; then
      echo "$file"
      break
    fi

    if grep -Eiq "^[[:space:]]*name:[[:space:]]*['\"]?${skill_name}['\"]?[[:space:]]*$" "$file"; then
      echo "$file"
      break
    fi
  done | head -n 1
}

install_skill() {
  local repo="$1"
  local skill_name="$2"
  local target_name="${3:-$2}"

  local skill_file
  skill_file="$(find_skill_file "$repo" "$skill_name" || true)"

  if [ -z "$skill_file" ]; then
    echo "SKIP: Could not find skill '$skill_name' in $repo"
    return 0
  fi

  local src_dir
  src_dir="$(dirname "$skill_file")"

  copy_dir "$src_dir" "$SKILLS_DIR/$target_name"
  echo "Installed: $skill_name -> .claude/skills/$target_name"
}

write_skill() {
  local skill_name="$1"
  local skill_dir="$SKILLS_DIR/$skill_name"

  mkdir -p "$skill_dir"
  cat > "$skill_dir/SKILL.md"
  echo "Wrote custom skill: .claude/skills/$skill_name"
}

log "Cloning/updating external skill repos"

clone_or_update "https://github.com/affaan-m/everything-claude-code" \
  "$CACHE_DIR/everything-claude-code"

clone_or_update "https://github.com/alirezarezvani/claude-skills" \
  "$CACHE_DIR/claude-skills"

clone_or_update "https://github.com/Orchestra-Research/AI-research-SKILLs" \
  "$CACHE_DIR/ai-research-skills"

clone_or_update "https://github.com/K-Dense-AI/scientific-agent-skills" \
  "$CACHE_DIR/scientific-agent-skills"

log "Installing selected third-party skills"

# Token/context discipline
install_skill "$CACHE_DIR/everything-claude-code" "strategic-compact"

# General engineering/code-quality skills
install_skill "$CACHE_DIR/claude-skills" "senior-ml-engineer"
install_skill "$CACHE_DIR/claude-skills" "senior-data-scientist"
install_skill "$CACHE_DIR/claude-skills" "code-reviewer"
install_skill "$CACHE_DIR/claude-skills" "adversarial-reviewer"
install_skill "$CACHE_DIR/claude-skills" "tdd-guide"

# ML research / MLOps skills
install_skill "$CACHE_DIR/ai-research-skills" "pytorch-lightning"
install_skill "$CACHE_DIR/ai-research-skills" "weights-and-biases"
install_skill "$CACHE_DIR/ai-research-skills" "sentence-transformers"

# Scientific/statistical ML skills
install_skill "$CACHE_DIR/scientific-agent-skills" "scikit-learn"
install_skill "$CACHE_DIR/scientific-agent-skills" "shap"
install_skill "$CACHE_DIR/scientific-agent-skills" "statsmodels"

log "Writing project-specific custom skills"

write_skill "token-discipline" <<'EOF'
---
name: token-discipline
description: Use when a task is long, repetitive, context-heavy, or at risk of wasting tokens. Keep work compact and create handoff summaries.
---

# Token Discipline

Use this skill for large coding, ML, debugging, and architecture tasks.

Rules:

1. Do not repeat code or explanations already visible in the repo.
2. Prefer targeted diffs, exact commands, and concise summaries.
3. Before large changes, inspect the current repo structure.
4. Keep status updates short.
5. After major milestones, create a compact handoff summary:
   - Current goal
   - Files changed
   - Commands run
   - Tests passed or failed
   - Remaining work
6. Do not paste full files unless explicitly requested.
7. Avoid huge scaffolds when a smaller working vertical slice is better.
8. Suggest `/compact` after exploration, debugging, or completing a major phase.
EOF

write_skill "ml-research-engineering" <<'EOF'
---
name: ml-research-engineering
description: Use for advanced ML modeling workflows including baselines, feature extraction, embeddings, training loops, evaluation, ablations, and research-quality experiment design.
---

# ML Research Engineering

Use this skill when building or improving ML models.

Workflow:

1. Define the task clearly:
   - input
   - output
   - prediction target
   - unit of analysis
   - train/validation/test split
   - leakage risks

2. Start with baselines:
   - simple statistical baseline
   - classical ML baseline
   - neural model only after the task is validated

3. Build the modeling pipeline:
   - data loading
   - preprocessing
   - feature extraction
   - model
   - training loop
   - evaluation script
   - artifact saving

4. Evaluate rigorously:
   - use metrics appropriate to the task
   - compare against baselines
   - inspect failure cases
   - avoid overclaiming

5. Improve scientifically:
   - change one variable at a time
   - run ablations
   - track configs and results
   - write down conclusions after each experiment

6. Code standards:
   - no hardcoded absolute paths
   - no hidden global state
   - no silent data mutation
   - functions should be testable
   - configs should be explicit
EOF

write_skill "mlops-production" <<'EOF'
---
name: mlops-production
description: Use for productionizing ML projects: reproducible training, data validation, experiment tracking, packaging, deployment, monitoring, and CI.
---

# MLOps Production

Prioritize production-grade ML engineering.

Check for:

1. Reproducibility
   - pinned dependencies
   - config-driven experiments
   - deterministic seeds where reasonable
   - clear train/eval/test splits

2. Data safety
   - raw data is never mutated
   - schema validation exists
   - leakage checks exist
   - missing-value handling is explicit

3. Training quality
   - baseline model first
   - meaningful metrics
   - error analysis
   - saved artifacts
   - run summaries

4. Evaluation
   - separate validation/test logic
   - calibration where useful
   - confidence/uncertainty where useful
   - failure case inspection

5. Packaging
   - clean source layout
   - CLI entrypoints
   - tests for parsing, preprocessing, inference, and metrics

6. Monitoring
   - experiment logs
   - model cards or run summaries
   - data drift checks for production-like workflows
EOF

write_skill "text-data-safety" <<'EOF'
---
name: text-data-safety
description: Use when working with raw conversation exports, text_data, private messages, HTML files, derived datasets, or relationship-analysis modeling.
---

# Text Data Safety

Rules:

1. Never modify files in `text_data/`.
2. Treat raw messages as private data.
3. Do not print large raw message excerpts unless explicitly requested.
4. Write derived data to `data/processed/` or another non-raw output directory.
5. Keep parsing, cleaning, feature extraction, modeling, and reports separated.
6. Add tests using tiny synthetic HTML/message fixtures, not private real messages.
7. Check for data leakage before training or evaluation.
8. Prefer aggregate statistics, de-identified examples, and reproducible pipelines.
EOF

write_skill "best-code-possible" <<'EOF'
---
name: best-code-possible
description: Use when writing, editing, refactoring, or reviewing code. Prioritize correctness, maintainability, tests, security, and clean architecture.
---

# Best Code Possible

When modifying code:

1. First understand the existing structure.
2. Prefer small, reviewable changes.
3. Keep functions focused and testable.
4. Avoid unnecessary abstractions.
5. Add or update tests when behavior changes.
6. Check edge cases and error handling.
7. Keep names clear and specific.
8. Avoid hidden state and surprising side effects.
9. Do not leave dead code, debug prints, or TODOs unless intentional.
10. Run the relevant tests or explain why they cannot be run.

Before finalizing, review:

- correctness
- edge cases
- security/privacy
- performance
- maintainability
- test coverage
EOF

log "Creating root CLAUDE.md if missing"

if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
  cat > "$PROJECT_ROOT/CLAUDE.md" <<'EOF'
# Claude Project Instructions

This is an ML/text-analysis repo.

Core rules:

1. Do not modify `text_data/`.
2. Treat raw conversation data as private.
3. Prefer small, testable, production-quality changes.
4. Use baselines before complex models.
5. Keep ML experiments reproducible and config-driven.
6. Prefer concise responses and targeted diffs.
7. Do not paste large raw data excerpts.
8. Use synthetic fixtures for tests.
9. Save derived outputs outside raw data directories.
10. Run relevant tests before finalizing changes.

Important repo-local skills:

- `text-data-safety`
- `ml-research-engineering`
- `mlops-production`
- `token-discipline`
- `best-code-possible`
EOF
  echo "Created CLAUDE.md"
else
  echo "CLAUDE.md already exists; leaving it unchanged."
fi

log "Installed skills"

find "$SKILLS_DIR" -maxdepth 2 -name SKILL.md -print | sort

log "Done"

echo ""
echo "Next steps:"
echo "  1. Review .claude/skills/*/SKILL.md"
echo "  2. Run: git add scripts/setup_claude_skills.sh .claude CLAUDE.md"
echo "  3. Run: git commit -m 'Add Claude Code skills setup'"
