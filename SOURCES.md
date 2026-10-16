# Technical references

Reviewed for the conference lab on October 15, 2026.

- GitHub OIDC and immutable subject claims: https://docs.github.com/en/actions/reference/security/oidc
- GitHub OIDC with AWS: https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- AWS policy evaluation: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- CloudFormation: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html

Local models are deliberately limited teaching aids. They do not validate JWT
signatures, implement the full IAM evaluation algorithm, or produce CloudTrail
events. Only an actual AWS run can establish the corresponding AWS results.
