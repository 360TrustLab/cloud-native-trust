# Technical references

- [AWS policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [Secrets Manager practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [Secret rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [S3 actions and resource ARNs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-policy-actions.html)

The local model supports Action/Resource matching and explicit deny precedence.
It rejects unsupported statement features. It does not implement the full IAM
evaluation algorithm or generate CloudTrail events. The Lambda probe records
actual AWS SDK results when deployed in a sandbox.
