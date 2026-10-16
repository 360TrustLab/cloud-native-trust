"""CRH07: limited identity-policy examples, not the AWS policy simulator."""
import argparse,fnmatch,json
from pathlib import Path
ROOT=Path(__file__).parent

def decision(policy,action,resource):
    """Subset only: Action/Resource glob matches, explicit deny overrides allow."""
    matched=[]
    for s in policy['Statement']:
        if set(s)-{'Sid','Effect','Action','Resource'}:raise ValueError('Unsupported policy feature in local teaching model')
        actions=s['Action'] if isinstance(s['Action'],list) else [s['Action']]
        resources=s['Resource'] if isinstance(s['Resource'],list) else [s['Resource']]
        if any(fnmatch.fnmatchcase(action.lower(),p.lower()) for p in actions) and any(fnmatch.fnmatchcase(resource,p) for p in resources):matched.append(s['Effect'])
    return 'DENY' if 'Deny' in matched or 'Allow' not in matched else 'ALLOW'

def evaluate():
    policies={stage:json.loads((ROOT/'policies'/f'{stage}.json').read_text()) for stage in ['before','after']}
    checks=[]
    cases=[
      ('Read intended document','s3:GetObject','arn:aws:s3:::360trustlab-synthetic/documents/example.txt'),
      ('Write application metadata','dynamodb:PutItem','arn:aws:dynamodb:us-east-1:000000000000:table/360trustlab-synthetic'),
      ('Read integration secret','secretsmanager:GetSecretValue','arn:aws:secretsmanager:us-east-1:000000000000:secret:360trustlab/integration-SYNTHETIC'),
      ('Read unrelated document','s3:GetObject','arn:aws:s3:::360trustlab-synthetic/unrelated/example.txt'),
      ('Read unrelated secret','secretsmanager:GetSecretValue','arn:aws:secretsmanager:us-east-1:000000000000:secret:360trustlab/unrelated-SYNTHETIC'),
    ]
    for name,action,resource in cases:
        checks.append({'name':name,'action':action,'resource':resource,**{stage:decision(policy,action,resource) for stage,policy in policies.items()}})
    return {'lab':'CRH07 · Cloud-native trust boundaries','scope':'LOCAL POLICY SUBSET MODEL · synthetic ARNs · no AWS requests',
      'secret_values_displayed':False,'identity':'Synthetic workload role; no static access keys',
      'checks':checks,'assertions':{'intended_operations_preserved':all(c['after']=='ALLOW' for c in checks[:3]),
       'unrelated_operations_denied':all(c['after']=='DENY' for c in checks[3:])}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='artifacts/report.json');a=p.parse_args();report=evaluate()
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    return 0 if all(report['assertions'].values()) else 1
if __name__=='__main__':raise SystemExit(main())
