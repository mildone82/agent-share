---
agent: anita
intel: lauran
timestamp: 2026-10-21T10:05:00+08:00
task_id: agenticworld-verification-skill-001
status: planned
source: outer-loop-intel + anita-verification-layer
target: linus / juha
repos:
  - mildone82/agenticworld
  - mildone82/agent-share
playbook: feature
default_branch: bootstrap
mission: 2026-10-21-agenticworld-verification-skill
---

# Mission: agenticworld-verification-skill

在 `mildone82/agenticworld`（首个 verification 落地仓）建立可重复的验证能力：agent 改完后必须用真实检查证明行为，而不是「构建绿了就算完成」。对齐 pstack Prove It Works。

> Anita 在 Lauran 情报草稿上补齐验证协议层；**无 AWS 凭证时的 BLOCKED vs SKIP 是本方案硬规则**。

## 1. 目标与非目标

### 目标

1. 新增项目内 verification skill/文档（建议 `.cursor/skills/verify-agenticworld/SKILL.md` 或 `docs/VERIFICATION.md`）：Launch / Doctor / Drive / Evidence / Cleanup。
2. 把现有 `deploy/aws/scripts/validate-deployment.sh` 纳入门禁，并写清 **无集群/无凭证** 时的判定（见 §2）。
3. 本地源码路径：`cd multica && make check`（或文档化最小替代）作为代码变更证据。
4. 在 `agent-share` 交一份 progress 模板，示范如何引用 evidence 文件。
5. Juha：把「缺 evidence 不得标 COMPLETE」编码进可机器检查的规则（可先 shell gate）。

### 非目标

- 不改 Multica 上游业务逻辑。
- **不创建真实 AWS 资源**；无凭证不得假装通过。
- 不自动 merge。
- 不在本 mission 实现全仓 formal verification。

## 2. 验收协议（Verification Protocol）

### 2.1 通用原则

- 每条证据含：`command`、`expect`、`artifact_path`、`result` ∈ `{pass, fail, skip, blocked, inconclusive}`、`last_run`。
- **FAIL**：命令应跑且失败 → 不得 COMPLETE。
- **INCONCLUSIVE**：环境异常无法判定 → 不得 COMPLETE。
- **SKIP / BLOCKED**：见下表；写入证据后，**仅当变更范围不依赖被跳过门禁** 才允许 COMPLETE。

### 2.2 无 AWS 凭证 / 无集群：BLOCKED vs SKIP（硬规则）

| 条件 | 判定 | 含义 | 可否 COMPLETE |
|------|------|------|----------------|
| 变更触及 `deploy/aws/**`、Helm/Terraform、或验证脚本本身，且缺少 AWS 凭证或可达集群 | **BLOCKED** | 必跑门禁无法执行，任务停 | **否**（除非 Human 书面豁免并改范围） |
| 变更仅为文档/注释/非部署路径（如只改 `README`），且 skill 声明部署门禁不适用 | **SKIP** | 门禁不适用，记录原因 | **是**（仍须跑适用的本地门禁） |
| 有凭证但集群不健康 / 脚本超时 | **BLOCKED** 或 **INCONCLUSIVE** | 不得记为 pass；优先 BLOCKED 若脚本明确失败 | **否** |
| `aws sts get-caller-identity` 失败 | 视为 **无凭证** | 进入上表 | 按上表 |
| Agent 伪造日志或跳过检测 | **FAIL（诚信）** | 发现即拒签 | **否** |

**探测命令（Doctor 段必须包含）：**

```bash
# 凭证探测（不打印密钥）
aws sts get-caller-identity >/tmp/aw-id.json 2>/tmp/aw-id.err
# exit 0 → 有凭证；非 0 → 无凭证（证据只保留 exit code + 错误类型，禁止贴 Secret）
```

**SKIP 证据最低要求：** `scope_paths`、`why_skip`、`detector_command`、`detector_exit_code`。

**BLOCKED 证据最低要求：** 同上 + `blocked_gate`（如 `validate-deployment.sh`）+ `next_human_action`（如何提供凭证/集群）。

### 2.3 按变更类型的证据矩阵

| 变更类型 | 必跑 | 无 AWS 时 |
|----------|------|-----------|
| 只改 README / 纯文档 | `make check` 可选；文档链接检查 | 部署门禁 **SKIP** |
| 改 Go/TS 应用代码（非 deploy） | `cd multica && make check` | 部署门禁 **SKIP** |
| 改 `deploy/aws/**` / validate 脚本 / Helm | `make check`（若适用）+ `validate-deployment.sh` | **BLOCKED** |
| 改 verification skill 自身 | skill `--self-test` 或最小 dry-run + 故意失败用例能被抓住 | 不要求真集群；自测 **必过** |

### V0 — 方案门禁

| ID | Pass |
|----|------|
| V0.1 | 本 plan 合入 `.acp/plan/` |
| V0.2 | 正文含 BLOCKED vs SKIP 表与探测命令 |
| V0.3 | 明确不创建真实 AWS 资源、不碰 secrets |

### V1 — Skill 落地

| ID | 检查 | Pass |
|----|------|------|
| V1.1 | skill/文档含 Launch, Doctor, Drive, Evidence, Cleanup | 五段齐全 |
| V1.2 | Doctor 含 AWS 探测且不泄露密钥 | 代码评审通过 |
| V1.3 | 故意破坏用例：缺 evidence → gate 失败 | `--self-test` 或等价证明 |
| V1.4 | 「只改 README」路径可 SKIP 部署门禁并 COMPLETE | 跑通一次，证据入库 |
| V1.5 | 「改 validate 脚本」路径无凭证 → BLOCKED，不得 COMPLETE | 跑通一次，证据入库 |

### V2 — agent-share 桥

| ID | Pass |
|----|------|
| V2.1 | progress 模板示范 evidence 链接 |
| V2.2 | Juha gate：缺 `evidence/summary.md`（或约定路径）→ 非 0 |

### V3 — 签核

| ID | Pass |
|----|------|
| V3.1 | Anita 审协议与两份示范证据（SKIP 例 + BLOCKED 例） |
| V3.2 | Juha 审机器规则 |
| V3.3 | merge 仅 Human |

**Done：** V0–V3；至少一份 SKIP 示范证据 + 一份 BLOCKED 示范证据已提交（可在 `agent-share` `.acp/evidence/`）。

## 3. 风险与回滚

| 风险 | 缓解 | 回滚 |
|------|------|------|
| Agent 把 BLOCKED 写成 SKIP | Juha gate 校验：触及 deploy 路径却无 AWS 探测 pass → 红 | 拒签 PR |
| 凭证泄露进日志 | 禁止 cat 密钥；证据只留 exit code | rotate（人工） |
| `make check` 过重 | 文档允许「最小替代」但须列出具体命令 | 收紧回 make check |
| 与 Multica 上游漂移 | skill 记录覆盖路径与 commit | maintain 另开 mission |

## 4. 实现约束

1. 默认分支 `bootstrap`。
2. 不碰 secrets；不创建 AWS 资源。
3. Engineer (Linus) ≠ Verifier (Juha)。
4. Cloud Agent 写 GitHub 需 Cursor access。
5. 先方案后代码。

## 5. 分步里程碑

| Step | 内容 | 负责人 |
|------|------|--------|
| M0 | 本 plan 合入 agent-share | Anita |
| M1 | skill 骨架 + Doctor AWS 探测 | Linus |
| M2 | 证据矩阵 + self-test（能抓住缺 evidence） | Linus |
| M3 | SKIP/BLOCKED 各一份示范证据 + Juha gate | Linus / Juha |
| M4 | Anita 签核 | Anita |

## 6. 开放问题

1. skill 落点：`.cursor/skills/verify-agenticworld/` 还是仅 `docs/VERIFICATION.md`？（建议两者：skill 调文档）
2. Human 豁免 BLOCKED 的书面格式放哪（issue 评论 vs evidence 文件）？
3. `make check` 失败但与变更无关时，是否允许标注 `inconclusive` 并拆 PR？

## Suggested owners

- Engineer: Linus
- Verifier: Juha
- Protocol/Evidence: Anita
- Coordinator: Mildone
- Intel: Lauran
