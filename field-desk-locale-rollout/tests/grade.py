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


def grade(checks):
    scores={category:0.0 for category in CATEGORIES}
    if 'infrastructure' not in checks:
        for category in CATEGORIES:
            names=[name for name,group in PLAN.items() if group==category]
            scores[category]=sum(checks.get(name,{}).get('passed') is True for name in names)/len(names)
    reward={'overall':sum(scores.values())/len(CATEGORIES),**scores}
    failed=[name for name in PLAN if checks.get(name,{}).get('passed') is not True]
    verdict={'all_checks_passed':not failed and 'infrastructure' not in checks,
             'all_critical_checks_passed':not any(name in CRITICAL for name in failed) and 'infrastructure' not in checks,
             'critical_failures':[name for name in failed if name in CRITICAL],
             'missing_checks':[name for name in PLAN if name not in checks],
             'infrastructure_error':'infrastructure' in checks,
             'note':'Overall is the equal-weight mean of four category pass fractions. A nonzero mean does not erase a critical failure.'}
    return reward,verdict
