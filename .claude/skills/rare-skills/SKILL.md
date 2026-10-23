---
name: rare-skills
description: Router to rarely needed service skills kept out of the default skill list - AWS (Bedrock, CDK, CloudFormation, IAM, Lambda/serverless, containers, databases, networking, storage, observability, billing, SDKs, sign-in), Cloudflare (Workers, Wrangler, Durable Objects, Agents SDK, Sandbox SDK, Email, Zero Trust, Turnstile) and web performance. Use when a task touches one of these services and no matching skill is loaded.
upstream: []
---

# rare-skills

The service skills live in `~/.agents/rare/<name>/`, out of the always-loaded list so they do not crowd every session. `setup-project` links the ones a repo uses into that repo's `.claude/skills/`, where they load on their own; this router reaches the rest.

## Use

1. Find the skill: `ls ~/.agents/rare`, or pick from the table.
2. Read `~/.agents/rare/<name>/SKILL.md` in full and follow it as if it had been invoked. Its references resolve relative to its own directory.
3. If the repo will keep needing it, suggest re-running `setup-project` to link it there.

| Domain | Skills |
| --- | --- |
| AWS, getting started | `signing-in-to-aws`, `launch-with-aws` |
| AWS AI | `amazon-bedrock`, `aws-ai-ml` |
| AWS infrastructure as code | `aws-cdk`, `aws-cloudformation`, `aws-blocks` |
| AWS compute and apps | `aws-compute`, `aws-containers`, `aws-serverless`, `aws-deployment`, `aws-messaging-and-streaming` |
| AWS data and network | `aws-database`, `aws-storage`, `aws-networking` |
| AWS security and identity | `aws-iam`, `aws-security`, `aws-auth` |
| AWS operations | `aws-observability`, `setting-up-cloudwatch-observability`, `aws-billing-and-cost-management` |
| AWS SDKs | `aws-sdk-python-usage`, `aws-sdk-js-v3-usage`, `aws-sdk-swift-usage` |
| Cloudflare platform | `cloudflare`, `wrangler`, `workers-best-practices`, `durable-objects` |
| Cloudflare building blocks | `agents-sdk`, `sandbox-sdk`, `cloudflare-email-service`, `turnstile-spin` |
| Cloudflare Zero Trust | `cloudflare-one`, `cloudflare-one-migrations` |
| Web performance | `web-perf` |

A skill missing from the table but present in the directory is still valid; read it the same way.
