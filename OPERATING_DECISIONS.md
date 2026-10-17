# Operating decisions for workload access

I start with a failure assumption: this component is compromised. What can it
reach, and what must continue working while the team contains it? That makes
workload identity a decision about reliability and recovery as well as access.

## One workload before a platform redesign

Record the document prefix, metadata operation, and integration secret the
workload needs. Identify who maintains the role and who owns the consumer.
Shared roles can make deployment convenient while making later permission
removal difficult. Start with a boundary the team can test and maintain.

The local model supports its documented Action/Resource subset. It is not a
full IAM evaluator. Use the separate Lambda probe to validate actual AWS
authorization in a dedicated sandbox. Keep setup errors separate from denials.
The stack does not configure CloudTrail data-event collection.

## Rotation includes the consumer

A hypothetical failure: the vault has a new credential, but the consumer keeps
using the old cached value. The rotation job is green while application requests
fail. Identify who notices the failure, who refreshes the consumer, and who can
restore the intended integration without exposing the credential in logs.

Automatic rotation and caching are not implemented by this lab. In the real
application, test the backing-service update, refresh behavior, old-credential
rejection, bounded retries, and recovery. A stable secret reference does not
remove that operating work.

## Narrowing access safely

Keep the same request set before and after the policy change. Required document,
metadata, and secret operations should survive. Unrelated resources should be
denied for the expected reason. Observe the rollout and prepare a reviewed
fallback that restores only the required operation.

Application authorization, network reach, resource policies, and workload grants
answer different questions. Validate their actual interaction, including KMS
access where customer-managed keys are used. Azure managed identity and Key
Vault support related goals but need their own authorization and recovery tests.

## Dependency decisions

The fictional parser scenario separates interim containment from the upgrade.
If a patch changes the API, name the owner of compatibility testing and the
person accepting any temporary exposure. A restricted route does not repair
the component. Keep its scope and expiry visible until the patch is validated.
