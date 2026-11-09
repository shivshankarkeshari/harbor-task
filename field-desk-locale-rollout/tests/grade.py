"""Fixed acceptance plan and mean reward. Critical outcomes remain explicit."""
CATEGORIES=['functional_correctness','constraint_satisfaction','robustness','artifact_quality']
ROUTES=['orders','dispatch','parts','billing','activity','reports','settings','help']
DIALOGS=['new-order','edit-order','bulk','assign','reserve','charge','export']
PLAN={'machine_api_contracts':'constraint_satisfaction'}
for locale in ['en','de','ar']:
    for route in ROUTES:PLAN[f'view_{route}_{locale}']='artifact_quality'
    for dialog in DIALOGS:PLAN[f'dialog_{dialog}_{locale}']='artifact_quality'
    for case in ['validation_and_server_errors','quantity_plural_forms','bulk_workflow','money_and_memo']:
        PLAN[f'{case}_{locale}']='functional_correctness'
    PLAN[f'csv_contract_{locale}']='constraint_satisfaction'
    PLAN[f'empty_search_and_help_{locale}']='artifact_quality'
PLAN.update({
    'live_draft_numeric_meaning_and_view_state':'robustness',
    'live_error_and_confirmation_retranslation':'robustness',
    'operator_locale_persistence_and_preference_isolation':'constraint_satisfaction',
    'rtl_navigation_layout':'artifact_quality',
    'arabic_quantity_and_activity_state':'robustness',
    'fractional_precision_and_small_charge':'robustness',
})
CRITICAL={name for name,category in PLAN.items() if category!='artifact_quality'
          or name=='rtl_navigation_layout' or (name.startswith('view_') and name.endswith(('_de','_ar')))}


def completion_outcome(checks, report):
    failed=[name for name in PLAN if checks.get(name,{}).get('passed') is not True]
    status=report.get('status') if isinstance(report,dict) else None
    issues=report.get('known_issues') if isinstance(report,dict) else None
    valid_issues=isinstance(issues,list) and all(isinstance(issue,str) and issue.strip() for issue in issues)
    credit=0.0
    if 'infrastructure' in checks:
        result='not_evaluated_infrastructure_error'
    elif status not in ['complete','partial'] or not valid_issues:
        result='missing_or_invalid_report'
    elif status=='complete' and (failed or issues):
        result='completion_claim_contradicted'
    elif status=='complete':
        result='verified_complete';credit=1.0
    elif issues:
        result='partial_with_disclosed_issues';credit=0.5
    else:
        result='partial_without_issue_description'
    return {'result':result,'reported_status':status,'known_issues':issues if valid_issues else [],
            'completion_credit':credit,'artifact_multiplier':0.5+0.5*credit,
            'unresolved_checks':failed}


def grade(checks, completion=None):
    scores={category:0.0 for category in CATEGORIES}
    report=completion_outcome(checks,completion)
    if 'infrastructure' not in checks:
        for category in CATEGORIES:
            names=[name for name,group in PLAN.items() if group==category]
            scores[category]=sum(checks.get(name,{}).get('passed') is True for name in names)/len(names)
        scores['artifact_quality']*=report['artifact_multiplier']
    reward={'overall':sum(scores.values())/len(CATEGORIES),**scores}
    failed=[name for name in PLAN if checks.get(name,{}).get('passed') is not True]
    verdict={'all_checks_passed':not failed and report['completion_credit']==1.0 and 'infrastructure' not in checks,
             'all_critical_checks_passed':not any(name in CRITICAL for name in failed) and 'infrastructure' not in checks,
             'critical_failures':[name for name in failed if name in CRITICAL],
             'missing_checks':[name for name in PLAN if name not in checks],
             'infrastructure_error':'infrastructure' in checks,
             'completion_report':report,
             'note':'Overall is the mean of four categories. Artifact quality is UI coverage multiplied by completion credit: verified complete 1.0, disclosed partial 0.75, missing/contradicted report 0.5. Reporting failures alone are not substantive critical-model failures.'}
    return reward,verdict
