# CRH07: Cloud-Native Trust Boundaries

I use this lab to ask what a compromised workload can reach and how a team can
narrow that access while preserving the intended application behavior. The
role needs a maintenance owner and a recovery path, just as the service does.

See [Operating decisions](OPERATING_DECISIONS.md) for permission removal,
consumer rotation, dependency tradeoffs, and recovery.

## Local rehearsal

```sh
python3 -m unittest discover -s tests -v
python3 lab.py
```

The local model checks only Action/Resource matching and explicit deny precedence
against synthetic ARNs. It rejects unsupported statement features. It does not
implement full IAM semantics, authenticate a workload, execute cloud requests,
or generate CloudTrail records. `artifacts/report.json` labels that boundary.

## Demo 1: trace a secret to its identity (10–12 minutes)

1. Inspect `app/lambda_function.py` and `infra/stack.json`.
2. Lambda environment stores secret ARNs, never secret values or static keys.
3. Inspect the intended access boundary: the integration secret should be
   accessible, and the unrelated secret should be denied after hardening.
   Those outcomes still need real-account validation. No code path logs either value.
4. Run the local policy comparison. With a sandbox, use the actual probe below.

## Demo 2: blast radius locally (10–12 minutes)

Run `python3 lab.py`, compare the before/after policy decisions, and inspect
which synthetic resources remain reachable. Use the included local captures as
fallback. These results establish only the local model's behavior.

### Local acceptance checks

The first backup slide focuses on the two secret reads. The second uses an
editable acceptance table instead of repeating the same before/after image.
The table reports actual local results from `lab.py` and `policies/after.json`:

| Operation checked | Local after result |
| --- | --- |
| Read intended document | ALLOW |
| Write application metadata | ALLOW |
| Read integration secret | ALLOW |
| Read unrelated document | DENY |
| Read unrelated secret | DENY |

The first three checks ask whether the intended application behavior survives.
The last two ask whether unrelated access is denied. These are results from
the limited local model, not verified AWS authorization. Rerun `python3 lab.py`
to inspect the actions and synthetic resource ARNs behind each result.

### Optional AWS sandbox extension (not yet validated)

The CloudFormation template and AWS probe scripts have not been deployed or
validated in a real AWS account. Complete the sandbox setup and probes before
demonstrating actual AWS authorization. The behavior below describes the
intended design, not verified cloud results.

The deployable stack includes IAM-authenticated API Gateway → Lambda → S3, DynamoDB, and Secrets Manager, plus a presenter-assumable role that can invoke
only this lab's Lambda. The `before` policy expands access only to other synthetic
resources in the same stack. The default is `after` (narrow).

## Optional AWS sandbox setup (not yet validated; dedicated account/profile required)

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-aws.txt
aws --profile YOUR_SANDBOX cloudformation deploy \
  --stack-name live360-cloud --template-file infra/stack.json \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides PermissionMode=before PresenterPrincipalArn=YOUR_IAM_USER_OR_ROLE_ARN
python scripts/aws_probe.py --profile YOUR_SANDBOX --expect before --seed
```

The deployment principal needs permission to deploy the listed resources; its
identity policy must also permit `sts:AssumeRole` on the output ProbeRole ARN.
For SSO/assumed credentials, supply the underlying IAM role ARN, not an STS
session ARN. Confirm region and account before deploying. Do not use a production
profile. The endpoint requires AWS IAM authentication and exposes only `/health`.
No cloud deployment has been run as part of the local rehearsal.

Update with the **same parameters and principal**, changing `PermissionMode=after`:

```sh
aws --profile YOUR_SANDBOX cloudformation deploy \
  --stack-name live360-cloud --template-file infra/stack.json \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides PermissionMode=after PresenterPrincipalArn=YOUR_IAM_USER_OR_ROLE_ARN
python scripts/aws_probe.py --profile YOUR_SANDBOX --expect after
```

Allow for IAM propagation, then rerun if needed. `aws_probe.py` rejects setup
errors rather than counting them as expected denials. It uses STS temporary
credentials, invokes the Lambda, and records real SDK success/AccessDenied
responses from its execution role, without recording any secret material.

CloudTrail data-event collection is **not** configured by this stack. Lambda/S3
SDK response evidence is not a CloudTrail log. If showing CloudTrail during the
live talk, explicitly configure scoped data events first and account for their
cost. Do not claim absence from management-event lookup proves no data access.

## Teardown

Using the explicit sandbox profile, remove the two seeded objects and any object
under this stack's bucket only. Delete the stack. S3 objects also expire after one
day, Lambda logs after seven days, and DynamoDB uses on-demand billing. Secrets
Manager deletion can have a recovery period. Check the dedicated account for
remaining lab resources and charges. Local reset simply reruns `python3 lab.py`.

See [SOURCES.md](SOURCES.md) for official references and model limits.

## Local screenshot viewer

Run `python3 viewer.py --port 8765`, then open http://127.0.0.1:8765.
The browser shows actual local lab output with its scope clearly labeled.
It is not an AWS Console or GitHub screenshot. Stop with Ctrl+C.
