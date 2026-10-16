"""Run only after explicit sandbox deployment. Never render secret values."""
import argparse,json
from pathlib import Path
import boto3
p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--stack',default='live360-cloud');p.add_argument('--expect',choices=['before','after'],required=True);p.add_argument('--seed',action='store_true');p.add_argument('--output',default='artifacts/aws-report.json');args=p.parse_args()
session=boto3.Session(profile_name=args.profile)
stack=session.client('cloudformation').describe_stacks(StackName=args.stack)['Stacks'][0]
out={o['OutputKey']:o['OutputValue'] for o in stack['Outputs']}
if args.seed:
    for key in ['documents/example.txt','unrelated/example.txt']:
        session.client('s3').put_object(Bucket=out['Bucket'],Key=key,Body=b'360TrustLab synthetic document\n')
creds=session.client('sts').assume_role(RoleArn=out['ProbeRoleArn'],RoleSessionName='live360-contained-probe')['Credentials']
probe=boto3.Session(aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'],region_name=session.region_name)
response=probe.client('lambda').invoke(FunctionName=out['FunctionName'],Payload=b'{}')
result=json.loads(response['Payload'].read())
if response.get('FunctionError'):raise SystemExit('Lambda failed; do not treat setup errors as authorization denials.')
expected=['ALLOW']*5 if args.expect=='before' else ['ALLOW']*3+['DENY']*2
result['expected_mode']=args.expect
result['assertions_passed']=[x['result'] for x in result.get('checks',[])]==expected
path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));raise SystemExit(0 if result['assertions_passed'] else 1)
