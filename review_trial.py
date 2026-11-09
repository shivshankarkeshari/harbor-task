#!/usr/bin/env python3
"""Post-run evidence audit for this original task. No LLM calls or trajectory score."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import runpy

ROOT=Path(__file__).resolve().parent
if ROOT.name=='evidence':ROOT=ROOT.parent.parent
TASK=ROOT/'field-desk-locale-rollout'
GRADING=runpy.run_path(str(TASK/'tests/grade.py'))


def consistency(run):
    """Recompute rewards and critical outcomes from the fixed acceptance plan."""
    plan=GRADING['PLAN'];checks=run['checks'];categories=GRADING['CATEGORIES']
    expected={category:sum(checks.get(name,{}).get('passed') is True for name,group in plan.items() if group==category)/sum(group==category for group in plan.values()) for category in categories}
    if 'infrastructure' in checks:expected=dict.fromkeys(categories,0.0)
    expected['overall']=sum(expected.values())/len(categories)
    reward_ok=set(run['reward'])==set(expected) and all(isinstance(run['reward'].get(key),(int,float)) and math.isclose(run['reward'][key],value,abs_tol=1e-9) for key,value in expected.items())
    failed={name for name in GRADING['CRITICAL'] if checks.get(name,{}).get('passed') is not True}
    return {'reward_matches_checks':reward_ok,
            'critical_report_matches_checks':set(run['critical'].get('critical_failures',[]))==failed,
            'complete_case_plan':set(checks)==set(plan)}


def frozen_source():
    manifest=ROOT/'dist/before-run-manifest.json'
    if not manifest.exists():manifest=TASK/'evidence/pre-run-manifest.json'
    if not manifest.exists():return {'verified':False,'reason':'Pre-run manifest unavailable; inspect the frozen archive.'}
    expected=json.loads(manifest.read_text())['task_file_sha256']
    changed=[name for name,digest in expected.items() if not (TASK/name).is_file() or hashlib.sha256((TASK/name).read_bytes()).hexdigest()!=digest]
    actual={str(path.relative_to(TASK)) for path in TASK.rglob('*') if path.is_file()
            and path.relative_to(TASK).parts[0]!='evidence' and '__pycache__' not in path.parts and path.name!='RUN_REPORT.md'}
    added=sorted(actual-set(expected))
    return {'verified':not changed and not added,'checked_files':len(expected),'changed_or_missing_files':changed,'unexpected_task_files':added}


def load(job):
    job=job.resolve()
    if not ((job/'result.json').is_file() and ((job/'verifier').is_dir() or (job/'checks.json').is_file())):
        trials=list(job.glob('*/result.json'))
        if len(trials)!=1:raise ValueError('Choose one completed Harbor job/trial: '+str(job))
        job=trials[0].parent
    base=job/'verifier' if (job/'verifier').is_dir() else job
    checks=base/'checks.json';critical=base/'critical-outcomes.json';reward=base/'reward.json'
    return {'path':job,'checks':json.loads(checks.read_text()) if checks.is_file() else {},
            'critical':json.loads(critical.read_text()) if critical.is_file() else {'all_checks_passed':False,'infrastructure_error':True,'missing_checks':['verifier did not run'],'critical_failures':[]},
            'reward':json.loads(reward.read_text()) if reward.is_file() else {'overall':None},
            'result':json.loads((job/'result.json').read_text())}


def audit(oracle,target):
    reference=oracle['critical'];observed=target['critical'];result=target['result']
    model=(result.get('agent_info',{}).get('model_info') or {}).get('name')
    harness=result.get('agent_info',{}).get('name')
    efforts=set()
    session_dir=target['path']/'agent/sessions'
    if not session_dir.exists():session_dir=target['path']/'sessions'
    for path in session_dir.rglob('*.jsonl'):
        for line in path.open():
            try:event=json.loads(line)
            except ValueError:continue
            if event.get('type')=='turn_context':efforts.add(event.get('payload',{}).get('effort'))
    high=bool(efforts) and efforts=={'high'}
    accepted=model in ['gpt-6.1-sol','claude-opus-5-5','opus-5-5'] and harness in ['codex','claude-code','claude']
    oracle_ok=reference['all_checks_passed'] and not oracle['result'].get('exception_info')
    errors=bool(result.get('exception_info')) or observed['infrastructure_error']
    failures=observed['critical_failures']
    control_consistency=consistency(oracle);target_consistency=consistency(target);frozen=frozen_source()
    if not oracle_ok:status='invalid_oracle_control'
    elif errors:status='setup_or_build_error_needs_triage'
    elif not all(control_consistency.values()) or not all(target_consistency.values()):status='inconsistent_grading_evidence_needs_triage'
    elif not frozen['verified']:status='frozen_source_needs_confirmation'
    elif observed['missing_checks']:status='incomplete_verifier_evidence'
    elif not accepted or not high:status='model_or_effort_needs_confirmation'
    elif observed['all_checks_passed']:status='target_passed_no_failure'
    elif not failures:status='partial_result_without_declared_critical_failure'
    else:status='critical_failure_observed_needs_reproduction_review'
    cases=[]
    for name in failures:
        item=target['checks'].get(name,{})
        evidence_root=target['path']/'verifier' if (target['path']/'verifier').is_dir() else target['path']
        cases.append({'check':name,'oracle_passed':oracle['checks'].get(name,{}).get('passed'),
            'error':item.get('error'),'evidence':[str(evidence_root/ref) for ref in item.get('evidence',[])]})
    labels={
        'wrong_hypothesis':'Needs an explicit hypothesis and a contradictory probe tied to the final artifact.',
        'incomplete_inspection':'Needs an omitted relevant workflow/dependency, not merely a file-read count.',
        'bad_state_tracking':'Needs before/after state and code showing lost or misinterpreted state.',
        'brittle_patch':'Needs a valid in-scope counterexample and passing oracle replay.',
        'skipped_verification':'Needs evidence of the verification performed and the missed case; absence alone is not proof.',
        'report_hallucination':'Needs an explicit claim contradicted by the same artifact/version.',
        'other_substantive_failure':'Needs a reproducible critical outcome violation and supported cause.',
    }
    weights={'Harbor compliance and reproducibility':20,'Fairness and solvability':20,'Verifier quality':20,
             'Long-horizon difficulty':15,'Evidence of frontier-model failure':15,'Originality and realism':10}
    return {'status':status,'model':model,'harness':harness,'high_reasoning_confirmed':high,
        'overall_mean':target['reward']['overall'],'critical_failure_count':len(failures),'cases':cases,
        'same_check_ids':set(oracle['checks'])==set(target['checks']),
        'grading_consistency':{'oracle':control_consistency,'target':target_consistency},
        'frozen_source':frozen,
        'failure_requirement_met':None if status=='critical_failure_observed_needs_reproduction_review' else False,
        'rubric':{name:{'maximum':weight,'reviewer_score':None} for name,weight in weights.items()},
        'reviewer_total_out_of_100':None,
        'cause_review':{name:{'assigned':False,'evidence_needed':evidence} for name,evidence in labels.items()},
        'validity_review':['Replay the failed case on the saved target artifact and the passing oracle.',
            'Confirm the frozen source/test hashes and public requirement.',
            'Inspect screenshots, visible text, form values and persisted state; exclude environment/verifier errors.',
            'Write a short factual cause analysis; do not infer or score mental states from the trajectory.'],
        'note':'Mean reward is partial credit, not a substitute for critical outcomes. Cause labels and the 100-point rubric require evidence-based reviewer judgment.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oracle',type=Path,required=True);parser.add_argument('--target',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report=audit(load(args.oracle),load(args.target));args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({key:report[key] for key in ['status','overall_mean','critical_failure_count','failure_requirement_met','reviewer_total_out_of_100']},indent=2))
