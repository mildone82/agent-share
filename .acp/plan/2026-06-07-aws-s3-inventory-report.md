---
agent: hermes-macbook
timestamp: 2026-06-07T08:55:00+08:00
task_id: aws-s3-inventory-report-001
status: pending
source: macbook-pro
target: hermes-mac-mini
---

# Task: AWS S3 Inventory Report

## Objective

Generate a structured inventory report of all S3 buckets in AWS China account `460592757249` (region `cn-north-1`).

## Requirements

- [ ] List all S3 buckets using `aws s3api list-buckets --region cn-north-1`
- [ ] For each bucket, retrieve:
  - [ ] Creation date
  - [ ] Region/location
  - [ ] Approximate object count (via `aws s3 ls` or `list-objects-v2`)
  - [ ] Storage class summary (if feasible)
- [ ] Output as Markdown table or JSON file
- [ ] Save result to `deliverables/2026-06-07-aws-s3-inventory-report.md`

## Constraints

- Use existing `aws-cn-cli` skill conventions
- Default region: `cn-north-1`
- Do not modify or delete any bucket contents
- If a bucket has > 1000 objects, use pagination (`--max-items` / `--starting-token`)

## Acceptance Criteria

- Report contains all bucket names
- Each bucket has at least: name, creation date, region
- Output file is committed and pushed to `agent-share`
- Status file in `.acp/status/` is updated to `completed`

## Context

Current AWS identity (from macbook-pro):
```json
{
  "UserId": "AIDAWWPLXXIAYAEAAB3AC",
  "Account": "460592757249",
  "Arn": "arn:aws-cn:iam::460592757249:user/mildone"
}
```

Sample bucket already verified accessible: `jyn-consul`
