# Quiet Riot — Distributed Multi-Account Scale-Out (Phase 4 design)

> Status: **design + scaffold**. The pluggable backend interface
> (`quiet_riot/core/backends.py`) and the local backend are implemented and
> tested. The distributed backend and its IaC are specified here and stubbed in
> code; full standup requires real worker accounts and is the next build phase.

## Why this exists

The fundamental limit on Quiet Riot is **not** the code — it's AWS API
throttling. A single account/region tops out around **~1,100 validation
calls/sec** (per the README's own benchmark). Adding threads past that just
trades successes for `ThrottlingException`s. The only way to go faster is to
spread the work across **many AWS accounts**, each contributing its own
~1,100 calls/sec from its own throttling bucket.

`N` worker accounts ≈ `N × 1,100` checks/sec. That is the entire point of this
phase.

## Target architecture

```
                 ┌──────────────────────────────────────────┐
                 │            Control plane (1 account)        │
                 │                                            │
  wordlist  ──▶  │  Sharder ──▶ SQS request queue (fan-out)   │
                 │                      │                      │
                 │   DynamoDB/S3 results ◀── aggregator        │
                 └───────────────────────┬────────────────────┘
                                         │  (cross-account SQS / assume-role)
            ┌───────────────┬────────────┼────────────┬───────────────┐
            ▼               ▼             ▼            ▼               ▼
       Worker acct 1   Worker acct 2   ...        Worker acct N
       Lambda workers  Lambda workers             Lambda workers
       run the SAME    (ECR-pub/SNS/               write hits back
       core enumerators ECR-priv checks)           to central results
```

- **Control plane** (the org-management account): shards the wordlist into
  batches, pushes batches onto an SQS queue, and aggregates results from a
  central DynamoDB table (or S3). This is where the existing FastAPI app and
  CLI live — they just point at a `DistributedBackend` instead of the
  `LocalThreadPoolBackend`.
- **Worker accounts**: each runs Lambda consumers triggered by SQS. Each worker
  provisions its own ECR-Public / ECR-Private / SNS resources (exactly what
  `ResourceManager` does today) and runs the **same** `ecrpubenum` /
  `snsenum` / `ecrprivenum` / `s3aclenum` checkers. Hits are written to the
  central results store. Each worker has its own throttling budget.
- **Aggregation**: central DynamoDB `ResultsTable` keyed by principal, or an S3
  prefix with one object per batch; the control plane streams results back to
  the user (CLI summary / dashboard SSE).

## How it plugs into the existing core

This phase does **not** fork the codebase. Everything routes through one
interface (`quiet_riot/core/backends.py`):

```python
class ExecutionBackend(Protocol):
    def run(self, wordlist_path, session, threads) -> list[str]: ...
```

- `LocalThreadPoolBackend` — wraps today's `loadbalancer.getter/threader`
  (single account, thread pool). This is the default and is fully implemented.
- `DistributedBackend` — shards the wordlist, fans out over SQS to worker
  accounts, and collects from the results store. Stubbed today.

`Scanner` selects a backend (config / env `QUIET_RIOT_BACKEND=local|distributed`).
Because both backends consume the same wordlist and return the same
`list[str]` of validated principals, the CLI, FastAPI, and library all work
unchanged regardless of backend.

## Salvage from the `dev` branch

The `dev`/`wes-refactor` branch already sketched this (under `infra/`):

- `infra/child_accounts/` — per-account CFN: an **SQS request queue**, a
  **Lambda execution role**, and Lambda workers (`ecrpubenum.py`, `snsenum.py`,
  …) plus a `lambda_function.py` dispatcher that logs to **DynamoDB**.
- `infra/org_mgmt_account/` — a Dockerized FastAPI control-plane API
  (`routers/live.py`, `routers/query.py`) and its CFN.

What to **keep**: the SQS-fan-out + Lambda-worker + DynamoDB-aggregation shape;
the per-account CFN split (control plane vs worker).

What to **fix before shipping** (it was an unfinished sketch):

1. `lambda_function.py` hardcodes `DYNAMODB_TABLE`, `SQS_QUEUE_URL`, … — move to
   environment variables wired by CFN, and it calls
   `iam.update_assume_role_policy` as a placeholder rather than the real
   ECR/SNS resource-policy technique. Replace its body with the **already-fixed
   core enumerators** from `quiet_riot/core/enumeration/` (import the package
   into the Lambda bundle) so workers and local share one implementation.
2. Add a dead-letter queue + visibility-timeout tuning so throttled batches are
   retried, not lost.
3. Cross-account access: control plane assumes a per-worker role (or workers
   own their SQS and the control plane is granted `sqs:SendMessage`); pin trust
   to the control-plane account only.
4. Idempotent result writes (DynamoDB conditional put on principal) so retried
   batches don't double-count.

## Build sequence

1. **Backend seam (done):** `ExecutionBackend` + `LocalThreadPoolBackend`; wire
   `Scanner` to select via `QUIET_RIOT_BACKEND` (local default). No behavior
   change.
2. **Worker image:** package `quiet_riot.core.enumeration` as a Lambda
   (container or zip). One handler consumes an SQS batch, provisions its
   resources once (cold start), runs the checkers, writes hits to the results
   store, and tears down on shutdown.
3. **Control plane:** sharder (`getter`-style chunking sized to worker count),
   SQS producer, results aggregator. Implement `DistributedBackend.run` to
   produce → poll-until-drained → return.
4. **IaC:** finish the two CFN stacks (control plane + worker), parameterized by
   account id / region / queue ARNs. A `StackSet` deploys the worker stack to
   every worker account in the org OU.
5. **Throughput test:** measure checks/sec vs worker count; confirm near-linear
   scaling until a shared limit (e.g. central DynamoDB write capacity) appears,
   then size that.

## Cost / safety / legal

- Each worker provisions and deletes ECR/SNS/S3 per run — the
  tracked-resource cleanup from Phase 3 must run in the Lambda's `finally` so a
  crashed worker doesn't leak billable resources. Add an org-wide sweeper
  (scheduled Lambda) that deletes orphaned `quiet-riot-*` resources older than
  N hours **per account** as a backstop.
- Scope worker IAM to exactly the create/set-policy/delete actions on
  ECR-pub/ECR-priv/SNS/S3 — no `*`.
- This is authorized-use tooling (enumeration against AWS's public validation
  behavior from accounts you own). Keep it that way: workers only ever act in
  accounts under your own org.

## Not doing (yet)

Real multi-account standup needs provisioned worker accounts and an org OU,
which is operator work outside this repo. The code seam and this design make
that a deployment exercise, not a redesign.
