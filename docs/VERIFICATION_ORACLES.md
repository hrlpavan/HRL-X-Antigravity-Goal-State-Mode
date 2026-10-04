# Deterministic Verification Oracles Guide (β(s) = 1)

In Feudal HRL, the agent's termination condition $\beta(s)$ cannot rely on autoregressive language tokens like *"I believe I have met all requirements."* Such self-reporting frequently hallucinates completion.

Instead, the **HRL X Antigravity Goal State Engine** delegates completion decisions to an array of **Deterministic Verification Oracles**.

---

## 1. The Mathematical Foundation

Let $\mathcal{O} = \{O_1, O_2, \dots, O_K\}$ be the set of $K$ verification oracles configured for a goal state. Each oracle executes an environmental evaluation command and returns an exit code:

$$\text{eval}(O_i) \rightarrow c_i \in \mathbb{Z}$$

The boolean oracle evaluation $v_i$ is defined as:
$$v_i = \mathbb{I}(c_i == 0)$$

The composite Goal State termination indicator $\beta(s)$ is strictly conjunctive:
$$\beta(s) = \bigwedge_{i=1}^{K} v_i = \prod_{i=1}^{K} v_i \in \{0, 1\}$$

* If $\beta(s) = 1$: The goal state is mathematically and empirically validated. Task completes.
* If $\beta(s) = 0$: At least one oracle has failed. Task execution continues or triggers backtracking.

---

## 2. Standard 4-Tier Oracle Architecture

| Oracle | Category | Purpose | Example Commands |
| :--- | :--- | :--- | :--- |
| **Oracle 1** | Build / Compilation | Validates structural integrity, AST validity, and typing. | `npm run build`<br>`cargo check`<br>`tsc --noEmit`<br>`go build ./...` |
| **Oracle 2** | Test Suites | Validates functional correctness and regression invariants. | `pytest tests/`<br>`npm test`<br>`go test -v ./...`<br>`cargo test` |
| **Oracle 3** | Lint & Style | Validates maintainability, code style, and security lints. | `npm run lint`<br>`ruff check .`<br>`flake8`<br>`golangci-lint run` |
| **Oracle 4** | Git Cleanliness | Ensures clean workspace, zero merge artifacts, no git diff errors. | `git diff --check`<br>`test -z "$(git status --porcelain)"` |

---

## 3. Language & Framework Cheat Sheet

### TypeScript / Node.js
```bash
# Oracle 1: Typecheck & Build
npx tsc --noEmit && npm run build

# Oracle 2: Tests
npm test -- --coverage=false --passWithNoTests=false

# Oracle 3: Lint
npm run lint

# Oracle 4: Git Cleanliness
git diff --check
```

### Python (FastAPI / Django / Data Science)
```bash
# Oracle 1: Syntax & Bytecode Compilation
python3 -m compileall -q src/

# Oracle 2: Tests
pytest -q tests/

# Oracle 3: Lint & Formatting
ruff check . && ruff format --check .

# Oracle 4: Git Cleanliness
git diff --check
```

### Go (Golang)
```bash
# Oracle 1: Build
go build ./...

# Oracle 2: Tests
go test -v -race ./...

# Oracle 3: Lint
golangci-lint run

# Oracle 4: Git Cleanliness
git diff --check
```

### Rust
```bash
# Oracle 1: Build Check
cargo check --all-targets

# Oracle 2: Tests
cargo test --all

# Oracle 3: Lint
cargo clippy -- -D warnings

# Oracle 4: Git Cleanliness
git diff --check
```

---

## 4. Advanced: Designing Custom Domain Oracles

Beyond standard compile/test/lint suites, you can define domain-specific oracles:

### 1. Latency & Performance Oracle
Ensures a feature does not introduce regressions:
```bash
python3 benchmarks/check_latency.py --max-p99-ms 15
```

### 2. Dependency Budget Oracle
Ensures no unauthorized dependencies were added:
```bash
test $(git diff package.json | grep '+   "' | wc -l) -eq 0
```

### 3. Coverage Threshold Oracle
Guarantees minimum branch coverage:
```bash
pytest --cov=src --cov-fail-under=85
```
