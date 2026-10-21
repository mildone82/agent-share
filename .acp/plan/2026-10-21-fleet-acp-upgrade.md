---
agent: anita
intel: lauran
timestamp: 2026-10-21T10:05:00+08:00
task_id: fleet-acp-upgrade-001
status: in_progress
source: outer-loop-intel + anita-verification-layer
target: mildone / juha / linus
repos:
  - mildone82/agent-share
playbook: feature
mission: 2026-10-21-fleet-acp-upgrade
depends_on:
  - 2026-10-21-fleet-acp-guardrails
---

# Mission: fleet-acp-upgrade

把 `agent-share` 的 ACP 从「单 Planner→Implementer→Delivery」升级为舰队可用的双环任务板：外环情报包、内环 Engineer/Verifier、Human-only merge，并与现有 Grok Bot 角色对齐。

> 本文件在 Lauran 情报草稿上由 Anita 补齐 6 点方案模板（验证协议优先）。实现须等姊妹 mission `fleet-acp-guardrails` 的 V1–V3 骨架可用，或与其并行但不得绕过「先方案后代码」。

## 1. 目标与非目标

### 目标

1. README / `.acp/CONTEXT.md` 增加舰队角色表：Lauran（情报）、Mildone（协调）、Anita（研究/验证协议）、Juha（架构护栏）、Linus（工程）、Human merge。
2. `plan/` 模板强制字段：动机/复现、范围外、验收标准、建议 playbook、建议 Engineer≠Verifier。
3. `status/` 样例：`YYYY-MM-DD-task-name-progress.md` 含状态枚举与证据链接。
4. `guardrails` 摘要指针：禁止自我合并、独立 Verifier、分歧/超时 halt（可链到 `/workspace/multiagent-collab-kit/` policy，若存在）。
5. 对过期任务 `2026-06-07-aws-s3-inventory-report.md` 给出明确 disposition（archive 或 reopen with owner）。
6. 与 `fleet-acp-guardrails` 的 buffer/CREW/evidence/acp-collab-lint **兼容不重复造轮**——本 mission 补「双环叙事与模板字段」，护栏机器规则以 guardrails + Juha 为准。

### 非目标

- 不接入 Cursor marketplace pstack 插件。
- 不自动 merge；不给 Cloud Agent 写产品业务代码。
- 不新建 GitHub Issue（除非用户明确要求）。
- 不重复实现 buffer 状态机 / lint CI（属 guardrails mission）。

## 2. 验收协议（Verification Protocol）

原则：报告成功必须附可复现证据；缺证据 → 不得标 COMPLETE。

### V0 — 方案门禁

| ID | 检查 | Pass |
|----|------|------|
| V0.1 | 本文件在 `.acp/plan/2026-10-21-fleet-acp-upgrade.md` | 路径+命名正确 |
| V0.2 | 六段齐全（目标/验收/风险/约束/里程碑/开放问题） | 齐全 |
| V0.3 | 声明依赖 `fleet-acp-guardrails` 或不绕过其门禁 | 正文可见 |

### V1 — 角色与模板

| ID | 检查 | Pass |
|----|------|------|
| V1.1 | README 或 CONTEXT 含角色表（6 角色） | 六名齐全 |
| V1.2 | plan 模板（`.acp/plan/_TEMPLATE.md` 或文档内嵌）含强制字段清单 | 含动机、范围外、验收、playbook、Engineer≠Verifier |
| V1.3 | status 样例文件存在且链到 evidence 路径字段 | 样例可读 |
| V1.4 | 过期 S3 plan 有 disposition 记录（status 或 archives） | 非静默 pending |

### V2 — Guardrails 指针

| ID | 检查 | Pass |
|----|------|------|
| V2.1 | 文档写明：禁止自我合并、独立 Verifier、halt 条件 | 三条可见 |
| V2.2 | 指向 Juha 可编码的规则路径（哪怕先是草案 md） | 路径存在 |

### V3 — 与 lint 兼容

| ID | 检查 | Pass |
|----|------|------|
| V3.1 | 新 plan/status 文件通过 `acp-collab-lint`（新文件 fail 级） | CI 绿或本地 lint 0 |
| V3.2 | 旧 S3 plan 若未迁移：仅 warn，不挡本 mission Done | 符合 Mildone 拍板 |

**Done：** V0–V3 Pass；Anita 签核协议/证据；Juha 签核机器规则草案；**merge 仅 Human**。

## 3. 风险与回滚

| 风险 | 缓解 | 回滚 |
|------|------|------|
| 与 guardrails 目录/字段冲突 | 本 mission 不改 buffer schema；字段扩展走 PR 评审 | 撤回模板字段 |
| 角色表与 ROSTER 双源 | README 角色表为叙述，ROSTER 为权威；注明以 `.acp/crew/ROSTER.md` 为准 | 删重复表 |
| 过期 S3 plan 误删上下文 | archive 保留原文，status 标 archived | 从 archives 恢复 |
| collab-kit 路径不存在 | 文档写「若存在则链，否则内嵌最小 halt 规则」 | 内嵌规则 |

## 4. 实现约束

1. 先验证协议后代码；PR 必须链接本 plan。
2. 不碰 secrets。
3. Engineer ≠ Verifier（Linus ≠ Juha）。
4. 提交前缀 `[Agent: …]`；merge 仅 Human。
5. Cloud Agent 写仓需 Cursor access。

## 5. 分步里程碑

| Step | 内容 | 负责人 |
|------|------|--------|
| M0 | 本 plan 合入 | Anita |
| M1 | 角色表 + plan 模板 + status 样例 | Linus |
| M2 | guardrails 指针 + 过期 S3 disposition | Linus；Juha review |
| M3 | Anita 证据签核 | Anita |

## 6. 开放问题

1. 过期 S3 plan：默认 **archive** 还是指定 owner reopen？（建议 archive）
2. plan 模板强制字段是否全部进入 lint fail，还是部分 warn？
3. 是否在本 mission 引入 `reviewers[]` 字段到 status 样例（与 guardrails 拍板对齐）？

## Suggested owners

- Coordinator: Mildone
- Engineer: Linus
- Verifier: Juha
- Protocol/Evidence: Anita
- Intel: Lauran
