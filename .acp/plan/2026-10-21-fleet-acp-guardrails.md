---
agent: anita
timestamp: 2026-10-21T10:00:00+08:00
task_id: fleet-acp-guardrails-001
status: in_progress
playbook: feature
source: grok-bot-anita
target: implementer
mission: 2026-10-21-fleet-acp-guardrails
---

# Mission: fleet-acp-guardrails

把 `mildone82/agent-share` 从「双机 Hermes 上下文交换」升级为 **pstack 风格多 agent 舰队任务板**：buffer 队列、CREW 角色、证据清单、ACP lint CI；并与 pstack verification 对齐。实现仓 `agenticworld` 与后续新建的 `mildone-fleet` **本 mission 只留对接接口，不实现业务代码**。

## 1. 目标与非目标

### 目标（本 mission 验收范围）

1. **目录与约定**：在 `agent-share` 落地舰队任务板目录骨架与命名规范（见 §4），兼容现有 `.acp/plan|status|deliverables|logs` 与 `contexts/`。
2. **CREW 角色契约**：用机器可读文件声明角色（Anita=方案/验证协议；实现者；Juha=架构护栏/lint；协调者 Mildone），以及「先方案后代码」门禁。
3. **Buffer 队列**：定义待认领 / 进行中 / 阻塞 / 待验证 / 完成 的队列文件格式与状态机，单任务单文件，可被 agent 无歧义读写。
4. **证据清单（Evidence）**：每个 mission 必须附带可执行的证据项（命令 + 期望结果），对齐 pstack「Prove It Works」——报告成功必须能复现证据，否则标 `inconclusive`。
5. **ACP lint CI**：GitHub Actions 对 `.acp/**` 与队列文件做结构 lint（必填 frontmatter、命名、禁止 secrets 形态、状态枚举合法）；失败即红。
6. **与 pstack verification 对齐的文档桥**：在 `.acp/` 写清如何把方案中的验收协议映射到后续 `verify-*` skill / CI，以及「写错就红」规则归属 Juha。

### 非目标（明确不做）

- 不创建或改写 `mildone-fleet` 仓库（仅预留对接点说明）。
- 不改 `agenticworld` 产品代码；仅允许在方案中引用其既有 ACP 概念（如 `acp_deliverable`）作为后续对接备注。
- 不引入任何 secrets、token、密钥文件；CI 不得打印或请求凭据。
- 不做 IDE Agent Client Protocol（Zed ACP）运行时实现；本处 **ACP = Agent Collaboration Protocol（本仓既有含义）**，与 pypi `acplint`（Agent Client Protocol）区分，CI 命名用 `acp-collab-lint` 避免混淆。
- 不自动 merge、不自动对实现仓开业务 PR。

## 2. 验收协议（Verification Protocol）

> 原则（pstack）：*"It compiles" is not evidence.* 每条必须可本地/CI 复现；实现者提交前自跑；Juha 的 lint 红线不可跳过。

### V0 — 方案门禁（本文件合入即过）

| ID | 检查 | Pass | Fail |
|----|------|------|------|
| V0.1 | 本文件位于 `.acp/plan/2026-10-21-fleet-acp-guardrails.md` | path 存在且 frontmatter `status` 合法 | 缺失或命名不符 |
| V0.2 | 含目标/非目标、验收、风险、约束、里程碑、开放问题六段 | 六段齐全 | 缺段 |
| V0.3 | 明确「先验证协议后代码」与 secrets 禁令 | 正文可见 | 缺失 |

### V1 — 目录与队列契约

| ID | 检查 | 命令/方式 | Pass |
|----|------|-----------|------|
| V1.1 | 新增目录存在 | `test -d .acp/buffer && test -d .acp/crew && test -d .acp/evidence && test -d .acp/schemas` | 全为 0 |
| V1.2 | CREW 清单可读 | `test -f .acp/crew/ROSTER.md` | 含 Anita / Juha / Mildone / Implementer 四角色职责 |
| V1.3 | Buffer 状态机文档 | `test -f .acp/buffer/README.md` | 状态集合 = `{queued,claimed,in_progress,blocked,awaiting_verify,complete,archived}` |
| V1.4 | 示例 mission 卡片 | 至少 1 个 `.acp/buffer/*.md` 样例（可用本 mission） | frontmatter 含 `mission_id,role_owner,status,plan_path,evidence_path` |
| V1.5 | Schema | `.acp/schemas/mission.schema.json`（或等价 YAML） | 对样例 `buffer` 文件校验通过 |

### V2 — 证据清单

| ID | 检查 | Pass |
|----|------|------|
| V2.1 | `.acp/evidence/2026-10-21-fleet-acp-guardrails.md` 存在 | 每条证据含：`command`、`expect`、`artifact_path`（可空）、`last_run` |
| V2.2 | 证据项覆盖 lint 自测 | 含「故意坏文件被 lint 抓住」与「干净树通过」各至少 1 条（对齐 pstack *able to fail*） |
| V2.3 | 实现 PR 描述必须粘贴证据表 | PR template 勾选或 CI comment 要求 | 无证据 → 不得标 COMPLETE |

### V3 — ACP collab lint CI

| ID | 检查 | Pass |
|----|------|------|
| V3.1 | `.github/workflows/acp-collab-lint.yml` 存在 | push/PR 触发 |
| V3.2 | Lint 脚本（建议 `scripts/acp_collab_lint.py`） | `--self-test`：植入 ≥3 个缺陷全部被抓；干净 fixture 通过 |
| V3.3 | 规则最小集 | (a) plan/buffer 文件名 `YYYY-MM-DD-*.md`；(b) 必填 frontmatter 键；(c) `status` 枚举；(d) 禁止匹配密钥形态 → fail；(e) 禁止在 `.acp/` 存放 `.env` |
| V3.4 | CI 红线 | workflow 内 ephemeral fixture 自测 | job 失败码非 0 |

### V4 — 文档桥

| ID | 检查 | Pass |
|----|------|------|
| V4.1 | `.acp/CONTEXT.md` 更新 | 舰队流程；区分本仓 ACP vs Zed ACP |
| V4.2 | `README.md` 更新 | buffer 认领 + 方案先于代码 |
| V4.3 | 对接附录 | agenticworld / mildone-fleet 占位 | 无 secrets |

**Done：** V0–V4 Pass；非实现者签核 `awaiting_verify → complete`。

## 3. 风险与回滚

命名混淆→`acp-collab-*`；过度设计→最小 schema+样例；lint 误杀旧文件→首版 warn；secrets→CI 拒绝；无 Cursor access→人工落仓；与 Juha 冲突→以 Juha 机器规则为准。

## 4. 实现约束

先方案后代码；不碰 secrets；目录边界：buffer/status、plan、evidence、crew；提交前缀 `[Agent: anita|implementer|juha]`；M1→M3。

## 5. 里程碑

M0 plan｜M1 骨架+ROSTER+样例卡｜M2 lint+workflow｜M3 evidence+文档｜M4 另开。关闭点 M0–M3。

## 6. 开放问题 — 已拍板（Mildone 2026-10-21；Yongnan 可改）

1. **多 owner**：允许 `role_owner` + `reviewers[]`，**执行权仍单一** `role_owner`。
2. **旧 plan**：首版 lint 对历史文件 **warn**，新文件 **fail**；另开迁移 mission。
3. **mildone-fleet**：与 M1–M3 **并行**（Origin 草稿已在建）；本 mission **只留对接附录**，不阻塞 Done。
4. **签核**：协议/证据 → **Anita**；目录/CI 机器规则 → **Juha**；**merge 仅 Human**。
5. **acp_deliverable**：M3 文档桥写映射表；字段硬对齐放 **M4**。

实现侧：等 Juha 草案 + Linus 认领 M1。Anita 在用户确认后重试把本 plan PR 进 `.acp/plan/`。


## Suggested playbook

`playbook: feature`. This mission lands the fleet board and guardrails only.

## Suggested owners

- Coordinator: Mildone
- Engineer: Linus
- Verifier: Juha
- Protocol/Evidence: Anita

Engineer (Linus) is not the Verifier (Juha). Merge is Human only.
