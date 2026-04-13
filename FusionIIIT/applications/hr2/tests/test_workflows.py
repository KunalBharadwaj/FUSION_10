from datetime import date, timedelta
from .conftest import WFTestBase
from applications.hr2.models import Constants, LeaveForm, LTCform, CPDAAdvanceform, Appraisalform

WORKFLOW_URL = "/hr2/api/workflow_action/"

def _specs():
    import os, yaml
    with open(os.path.join(os.path.dirname(__file__), "specs", "workflows.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)["workflows"]

class HR2MasterRegistryWorkflowTests(WFTestBase):
    def _workflow(self, action, payload=None):
        self.login_as_faculty()
        return self.api_post(WORKFLOW_URL, {"action": action, "payload": payload or {}}, expected_status=None)
    def _leave(self):
        return LeaveForm.objects.create(employeeId=self.employee.id, name="Registry Employee", designation=self.employee.designation, submissionDate=date.today(), pfNo=101, departmentInfo="CSE", natureOfLeave="casual_leave", leaveStartDate=date.today()+timedelta(days=5), leaveEndDate=date.today()+timedelta(days=6), purposeOfLeave="Workflow", addressDuringLeave="Jabalpur", status=Constants.Status.PENDING, created_by=self.faculty_user)
    def _appraisal(self):
        return Appraisalform.objects.create(employeeId=self.employee.id, name="Registry Employee", designation=self.employee.designation, submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user)
    def _ltc(self):
        return LTCform.objects.create(employeeId=self.employee.id, name="Registry Employee", blockYear="2024-2026", pfNo=101, designation=self.employee.designation, departmentInfo="CSE", addressDuringLeave="Jabalpur", submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user)
    def _cpda(self):
        return CPDAAdvanceform.objects.create(employeeId=self.employee.id, name="Registry Employee", designation=self.employee.designation, pfNo=101, purpose="Conference", amountRequired=1000, submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user)
    def _execute(self, wf_id, negative):
        if wf_id == "HR-WF-001":
            form = self._appraisal(); r = self._workflow("review_appraisal", {"form_id": form.id}); self._add_step(1, "route appraisal", "FORWARDED", f"HTTP {r.status_code}", r.status_code == 200)
            r = self._workflow("appraisal_decision", {"form_id": form.id, "decision": "REJECT" if negative else "APPROVE"}); form.refresh_from_db()
        elif wf_id == "HR-WF-002":
            form = self._leave(); r = self._workflow("hod_decision", {"form_id": form.id, "decision": "REJECT" if negative else "APPROVE", "remarks": "Rejected with sufficient detail"})
            form.refresh_from_db()
        elif wf_id == "HR-WF-003":
            form = self._ltc(); r = self._workflow("verify_ltc_claim", {"form_id": form.id}); self._add_step(1, "verify LTC", "FORWARDED", f"HTTP {r.status_code}", r.status_code == 200)
            r = self._workflow("ltc_decision", {"form_id": form.id, "decision": "REJECT" if negative else "APPROVE"}); form.refresh_from_db()
            if not negative: f = self._workflow("process_financial_claim", {"form_id": form.id, "claim_type": "LTC"}); self._add_step(3, "finance handoff", "recorded", f"HTTP {f.status_code}", f.status_code == 200)
        else:
            form = self._cpda(); r = self._workflow("verify_cpda_claim", {"target_type": "cpda_advance", "form_id": form.id}); self._add_step(1, "verify CPDA", "FORWARDED", f"HTTP {r.status_code}", r.status_code == 200)
            r = self._workflow("cpda_decision", {"target_type": "cpda_advance", "form_id": form.id, "decision": "REJECT" if negative else "APPROVE"}); form.refresh_from_db()
            if not negative: f = self._workflow("process_financial_claim", {"form_id": form.id, "claim_type": "CPDA"}); self._add_step(3, "finance handoff", "recorded", f"HTTP {f.status_code}", f.status_code == 200)
        expected = Constants.Status.REJECTED if negative else Constants.Status.APPROVED
        self._add_step(2, "decision", expected, form.status, r.status_code == 200 and form.status == expected)
        return form.status

def _make(wf, negative):
    def test(self):
        self._test_id, self._wf_id = f"{wf['id']}-{'NEG' if negative else 'E2E'}-01", wf["id"]
        self._test_category = "Negative" if negative else "End-to-End"
        case = wf["negative_tests"][0] if negative else wf["e2e_tests"][0]
        self._scenario, self._expected_final_state = case["scenario"], case["expected_final_state"]
        actual = self._execute(wf["id"], negative)
        self._record_result(f"Final state: {actual}", "Pass" if self._all_steps_passed() else "Fail")
    return test

for _wf in _specs():
    setattr(HR2MasterRegistryWorkflowTests, f"test_{_wf['id'].lower().replace('-', '_')}_e2e_01", _make(_wf, False))
    setattr(HR2MasterRegistryWorkflowTests, f"test_{_wf['id'].lower().replace('-', '_')}_negative_01", _make(_wf, True))
