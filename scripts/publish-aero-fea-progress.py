"""Update only the sanitized status file through this site's existing deploy.

Never touches runtime files, starts model work, force-pushes, publishes raw logs,
or includes unrelated staged changes. Stop on any publishing/auth failure.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TARGET='public/demos/aero/fea-diagnostic-progress/status.json'


def git(*args):
    result=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,text=True,timeout=90,
        env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='Never'))
    if result.returncode:raise RuntimeError('Website publishing failed: '+result.stderr[-1500:])
    return result.stdout.strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True,type=Path)
    args=parser.parse_args()
    if git('branch','--show-current')!='main':raise RuntimeError('Expected existing website main branch')
    if git('remote','get-url','origin')!='https://github.com/alexthegreat714/alex-blythe-site.git':
        raise RuntimeError('Website origin changed')
    git('ls-files','--error-unmatch',TARGET)
    result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/aero-fea-progress.py'),'--run',str(args.run),'--write'],
        cwd=ROOT,capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError(result.stderr[-1500:])
    if not git('diff','HEAD','--',TARGET):
        print(json.dumps({'state':'NO_PUBLIC_SNAPSHOT_CHANGE'}));return
    # --only commits only this path, preserving all unrelated work and staging.
    git('add','--',TARGET)
    git('commit','--only','-m','Update AeroFEA public progress snapshot','--',TARGET)
    commit=git('rev-parse','HEAD')
    git('push','origin','HEAD:main')
    print(json.dumps({'state':'WEBSITE_SNAPSHOT_PUSHED_DEPLOYMENT_PENDING','commit':commit,
                      'interpretation':'Existing static website deployment; verify deployed data separately.'}))


if __name__=='__main__':main()
