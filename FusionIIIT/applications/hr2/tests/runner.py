"""
Custom Django Test Runner for HR2 Module.
Generates 7 CSV report files after all tests complete.

Usage:
  python manage.py test applications.hr2.tests -v 2 \\
    --testrunner=applications.hr2.tests.runner.ReportingTestRunner
"""
import csv
import os
import yaml
from datetime import datetime
from django.test.runner import DiscoverRunner

# Import the shared results list from conftest
from applications.hr2.tests.conftest import _TEST_RESULTS

REPORTS_DIR = os.path.join(
    os.path.dirname(__file__), 'reports'
)
SPECS_DIR = os.path.join(
    os.path.dirname(__file__), 'specs'
)


def _load_yaml(filename):
    path = os.path.join(SPECS_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _count_designed_tests(specs, test_type):
    """Count how many tests are designed in YAML specs."""
    count = 0
    if test_type == 'UC':
        for uc in specs.get('use_cases', []):
            count += len(uc.get('happy_paths', []))
            count += len(uc.get('alternate_paths', []))
            count += len(uc.get('exception_paths', []))
    elif test_type == 'BR':
        for br in specs.get('business_rules', []):
            count += len(br.get('valid_tests', []))
            count += len(br.get('invalid_tests', []))
    elif test_type == 'WF':
        for wf in specs.get('workflows', []):
            count += len(wf.get('e2e_tests', []))
            count += len(wf.get('negative_tests', []))
    return count


def _determine_uc_status(tests):
    if not tests:
        return 'Not Implemented'
    statuses = [t['status'] for t in tests]
    if all(s == 'Pass' for s in statuses):
        return 'Implemented Correctly'
    if any(s == 'Pass' for s in statuses):
        return 'Partially Implemented'
    return 'Incorrectly Implemented'


def _determine_br_status(tests):
    if not tests:
        return 'Not Enforced'
    statuses = [t['status'] for t in tests]
    if all(s == 'Pass' for s in statuses):
        return 'Enforced Correctly'
    if any(s == 'Pass' for s in statuses):
        return 'Partially Enforced'
    return 'Incorrectly Enforced'


def _determine_wf_status(tests):
    if not tests:
        return 'Missing'
    statuses = [t['status'] for t in tests]
    if all(s == 'Pass' for s in statuses):
        return 'Complete'
    if any(s == 'Pass' for s in statuses):
        return 'Partial'
    return 'Incorrect'


class ReportingTestRunner(DiscoverRunner):

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # Clear results from previous runs
        _TEST_RESULTS.clear()

        result = super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)

        # Generate reports after tests complete
        os.makedirs(REPORTS_DIR, exist_ok=True)
        self._generate_reports()

        print(f"\n{'='*60}")
        print(f"  Reports written to: {REPORTS_DIR}")
        print(f"{'='*60}\n")

        return result

    def _generate_reports(self):
        uc_specs = _load_yaml('use_cases.yaml')
        br_specs = _load_yaml('business_rules.yaml')
        wf_specs = _load_yaml('workflows.yaml')

        results = list(_TEST_RESULTS)

        # ── Separate by type ───────────────────────────────────────────────
        uc_results = [r for r in results if r['source_type'] == 'UC']
        br_results = [r for r in results if r['source_type'] == 'BR']
        wf_results = [r for r in results if r['source_type'] == 'WF']

        # ── Count specs ────────────────────────────────────────────────────
        num_ucs = len(uc_specs.get('use_cases', []))
        num_brs = len(br_specs.get('business_rules', []))
        num_wfs = len(wf_specs.get('workflows', []))
        req_uc = num_ucs * 3
        req_br = num_brs * 2
        req_wf = num_wfs * 2
        des_uc = _count_designed_tests(uc_specs, 'UC')
        des_br = _count_designed_tests(br_specs, 'BR')
        des_wf = _count_designed_tests(wf_specs, 'WF')

        total_exec = len(results)
        total_pass = sum(1 for r in results if r['status'] == 'Pass')
        total_partial = sum(1 for r in results if r['status'] == 'Partial')
        total_fail = sum(1 for r in results if r['status'] == 'Fail')
        pass_rate = round(total_pass / total_exec * 100, 1) if total_exec else 0
        uc_adequacy = round(des_uc / req_uc * 100, 1) if req_uc else 0
        br_adequacy = round(des_br / req_br * 100, 1) if req_br else 0
        wf_adequacy = round(des_wf / req_wf * 100, 1) if req_wf else 0

        # ── Sheet 1: Module_Test_Summary ───────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'Module_Test_Summary.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerows([
                ['Metric', 'Value'],
                ['Module', 'HR2 (Human Resources)'],
                ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M')],
                ['LLM Used', 'GPT-5.3 Codex'],
                ['', ''],
                ['Total Use Cases', num_ucs],
                ['Total Business Rules', num_brs],
                ['Total Workflows', num_wfs],
                ['', ''],
                ['Required UC Tests', req_uc],
                ['Designed UC Tests', des_uc],
                ['Required BR Tests', req_br],
                ['Designed BR Tests', des_br],
                ['Required WF Tests', req_wf],
                ['Designed WF Tests', des_wf],
                ['', ''],
                ['UC Adequacy %', f'{uc_adequacy}%'],
                ['BR Adequacy %', f'{br_adequacy}%'],
                ['WF Adequacy %', f'{wf_adequacy}%'],
                ['', ''],
                ['Total Tests Executed', total_exec],
                ['Total Pass', total_pass],
                ['Total Partial', total_partial],
                ['Total Fail', total_fail],
                ['Strict Pass Rate %', f'{pass_rate}%'],
            ])

        # ── Sheet 2: UC_Test_Design ────────────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'UC_Test_Design.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Test ID', 'UC ID', 'Test Category', 'Scenario', 'Preconditions', 'Input / Action', 'Expected Result'])
            for uc in uc_specs.get('use_cases', []):
                uid = uc['id']
                for p in uc.get('happy_paths', []):
                    w.writerow([f"{uid}-HP-{uc.get('happy_paths', []).index(p)+1:02d}", uid, 'Happy Path',
                                p.get('scenario', ''), p.get('preconditions', ''), p.get('input_action', ''), p.get('expected_result', '')])
                for i, p in enumerate(uc.get('alternate_paths', []), 1):
                    w.writerow([f"{uid}-AP-{i:02d}", uid, 'Alternate Path',
                                p.get('scenario', ''), p.get('preconditions', ''), p.get('input_action', ''), p.get('expected_result', '')])
                for i, p in enumerate(uc.get('exception_paths', []), 1):
                    w.writerow([f"{uid}-EX-{i:02d}", uid, 'Exception',
                                p.get('scenario', ''), p.get('preconditions', ''), p.get('input_action', ''), p.get('expected_result', '')])

        # ── Sheet 3: BR_Test_Design ────────────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'BR_Test_Design.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Test ID', 'BR ID', 'Test Category', 'Input / Action', 'Expected Result'])
            for br in br_specs.get('business_rules', []):
                bid = br['id']
                for i, t in enumerate(br.get('valid_tests', []), 1):
                    w.writerow([f"{bid}-V-{i:02d}", bid, 'Valid', t.get('input_action', ''), t.get('expected_result', '')])
                for i, t in enumerate(br.get('invalid_tests', []), 1):
                    w.writerow([f"{bid}-I-{i:02d}", bid, 'Invalid', t.get('input_action', ''), t.get('expected_result', '')])

        # ── Sheet 4: WF_Test_Design ────────────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'WF_Test_Design.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Test ID', 'WF ID', 'Test Category', 'Scenario', 'Expected Final State'])
            for wf in wf_specs.get('workflows', []):
                wid = wf['id']
                for i, t in enumerate(wf.get('e2e_tests', []), 1):
                    w.writerow([f"{wid}-E2E-{i:02d}", wid, 'End-to-End', t.get('scenario', ''), t.get('expected_final_state', '')])
                for i, t in enumerate(wf.get('negative_tests', []), 1):
                    w.writerow([f"{wid}-NEG-{i:02d}", wid, 'Negative', t.get('scenario', ''), t.get('expected_final_state', '')])

        # ── Sheet 5: Test_Execution_Log ────────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'Test_Execution_Log.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Test ID', 'Source Type', 'Source ID', 'Expected Result', 'Actual Result', 'Status', 'Evidence', 'Tester'])
            for r in results:
                w.writerow([r['test_id'], r['source_type'], r['source_id'],
                             r['expected_result'], r['actual_result'],
                             r['status'], r['evidence'], r['tester']])

        # ── Sheet 6: Defect_Log ────────────────────────────────────────────
        failed = [r for r in results if r['status'] in ('Fail', 'Partial')]
        severity_map = {'UC': 'High', 'BR': 'Critical', 'WF': 'High'}
        with open(os.path.join(REPORTS_DIR, 'Defect_Log.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Defect ID', 'Related Test ID', 'Related Artifact', 'Severity', 'Description', 'Suggested Fix'])
            for i, r in enumerate(failed, 1):
                sev = 'Critical' if r['status'] == 'Fail' else 'Medium'
                w.writerow([
                    f"DEF-{i:03d}",
                    r['test_id'],
                    r['source_id'],
                    sev,
                    f"{r['source_type']} {r['source_id']}: Expected [{r['expected_result']}] but got [{r['actual_result']}]",
                    f"Review and fix implementation of {r['source_id']} — {r['evidence'][:200]}",
                ])

        # ── Sheet 7: Artifact_Evaluation ──────────────────────────────────
        with open(os.path.join(REPORTS_DIR, 'Artifact_Evaluation.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['Artifact ID', 'Artifact Type', 'Tests', 'Pass', 'Partial', 'Fail', 'Final Status', 'Remarks'])

            # UCs
            for uc in uc_specs.get('use_cases', []):
                uid = uc['id']
                tr = [r for r in uc_results if r['source_id'] == uid]
                pas = sum(1 for r in tr if r['status'] == 'Pass')
                par = sum(1 for r in tr if r['status'] == 'Partial')
                fai = sum(1 for r in tr if r['status'] == 'Fail')
                status = _determine_uc_status(tr)
                w.writerow([uid, 'UC', len(tr), pas, par, fai, status, uc.get('title', '')])

            # BRs
            for br in br_specs.get('business_rules', []):
                bid = br['id']
                tr = [r for r in br_results if r['source_id'] == bid]
                pas = sum(1 for r in tr if r['status'] == 'Pass')
                par = sum(1 for r in tr if r['status'] == 'Partial')
                fai = sum(1 for r in tr if r['status'] == 'Fail')
                status = _determine_br_status(tr)
                w.writerow([bid, 'BR', len(tr), pas, par, fai, status, br.get('title', '')])

            # WFs
            for wf in wf_specs.get('workflows', []):
                wid = wf['id']
                tr = [r for r in wf_results if r['source_id'] == wid]
                pas = sum(1 for r in tr if r['status'] == 'Pass')
                par = sum(1 for r in tr if r['status'] == 'Partial')
                fai = sum(1 for r in tr if r['status'] == 'Fail')
                status = _determine_wf_status(tr)
                w.writerow([wid, 'WF', len(tr), pas, par, fai, status, wf.get('title', '')])
