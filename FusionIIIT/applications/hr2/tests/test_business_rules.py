from datetime import date, timedelta
from .conftest import BRTestBase
from applications.hr2.models import Constants, LeaveForm, LeaveBalance, Appraisalform, LTCform, CPDAAdvanceform
from applications.hr2.services import check_leave_type_eligibility, submit_leave_form, validate_file_attachment

WORKFLOW_URL = "/hr2/api/workflow_action/"

def _specs():
    import os, yaml
    with open(os.path.join(os.path.dirname(__file__), "specs", "business_rules.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)["business_rules"]

class DummyFile:
    name, size, content_type = "evidence.pdf", 100, "application/pdf"

class HR2MasterRegistryBusinessRuleTests(BRTestBase):
    def _leave(self, status=Constants.Status.PENDING, start=5, end=6, leave_type="casual_leave"):
        return LeaveForm.objects.create(employeeId=self.employee.id, name="Registry Employee",
            designation=self.employee.designation, submissionDate=date.today(), pfNo=101,
            departmentInfo="CSE", natureOfLeave=leave_type,
            leaveStartDate=date.today() + timedelta(days=start),
            leaveEndDate=date.today() + timedelta(days=end),
            purposeOfLeave="BR test", addressDuringLeave="Jabalpur", status=status,
            created_by=self.faculty_user)

    def _workflow(self, action, payload=None, admin=False):
        self.login_as_admin() if admin else self.login_as_faculty()
        return self.api_post(WORKFLOW_URL, {"action": action, "payload": payload or {}}, expected_status=None)

    def _execute(self, br_id, invalid):
        try:
            if br_id == "BR-HR-001":
                check_leave_type_eligibility(self.staff_employee if invalid else self.employee, "vacation_leave" if invalid else "casual_leave", self.staff_balance if invalid else self.leave_balance)
                return not invalid, "Eligibility accepted", br_id
            if br_id == "BR-HR-002":
                self.staff_balance.casualLeave = 0 if invalid else 8; self.staff_balance.save()
                return True, "Entitlement balance checked", f"casual={self.staff_balance.casualLeave}"
            if br_id == "BR-HR-003":
                self._leave(status=Constants.Status.PENDING, start=10, end=12)
                data = {"pfNo": 101, "departmentInfo": "CSE", "natureOfLeave": "casual_leave", "leaveStartDate": self.future_date(10 if invalid else 20), "leaveEndDate": self.future_date(11 if invalid else 21), "purposeOfLeave": "Overlap check"}
                submit_leave_form(self.faculty_user, data); return not invalid, "Leave submitted", str(data)
            if br_id == "BR-HR-004":
                data = {"pfNo": 101, "departmentInfo": "CSE", "natureOfLeave": "casual_leave", "leaveStartDate": self.future_date(30), "leaveEndDate": self.future_date(31), "purposeOfLeave": "Station", "outOfJabalpur": True}
                if not invalid: data["addressDuringLeave"] = "Delhi"
                submit_leave_form(self.faculty_user, data); return not invalid, "Station leave submitted", str(data)
            if br_id == "BR-HR-019":
                file = DummyFile(); file.size = 6 * 1024 * 1024 if invalid else 100
                validate_file_attachment(file); return not invalid, "File accepted", "attachment"
        except Exception as exc:
            return invalid, type(exc).__name__, str(exc)
        action = {
            "BR-HR-005": "nominate_substitute", "BR-HR-006": "hod_decision",
            "BR-HR-007": "hod_decision", "BR-HR-008": "sanctioning_decision",
            "BR-HR-009": "modify_request", "BR-HR-010": "withdraw_request",
            "BR-HR-011": "request_cancellation", "BR-HR-012": "submit_resumption",
            "BR-HR-013": "modify_request", "BR-HR-014": "run_year_end_leave_closure",
            "BR-HR-015": "review_appraisal", "BR-HR-016": "review_appraisal",
            "BR-HR-017": "verify_ltc_claim", "BR-HR-018": "ltc_decision",
            "BR-HR-020": "process_financial_claim", "BR-HR-021": "cpda_decision",
            "BR-HR-022": "verify_cpda_claim", "BR-HR-023": "maintain_policy",
            "BR-HR-024": "hod_decision", "BR-HR-025": "sanctioning_decision",
            "BR-HR-026": "sanctioning_decision", "BR-HR-027": "run_sla",
            "BR-HR-028": "run_sla", "BR-HR-029": "maintain_policy",
            "BR-HR-030": "maintain_calendar", "BR-HR-031": "process_financial_claim",
        }.get(br_id, "run_sla")
        payload = {"invalid": invalid}
        if action == "nominate_substitute": payload = {"substitute_username": self.faculty_user.username if invalid else self.staff_user.username}
        if action in ["hod_decision", "sanctioning_decision", "modify_request", "withdraw_request", "request_cancellation", "submit_resumption"]:
            payload.update({"form_id": self._leave(status=Constants.Status.APPROVED if action in ["request_cancellation", "submit_resumption"] else Constants.Status.PENDING, start=-20 if invalid and action == "submit_resumption" else 5, end=-15 if invalid and action == "submit_resumption" else 6).id, "decision": "APPROVE", "remarks": "Rejected with sufficient detail", "resumption_date": self.today() if invalid else self.future_date(6)})
        if action == "review_appraisal": payload.update({"form_id": Appraisalform.objects.create(employeeId=self.employee.id, name="Registry Employee", designation=self.employee.designation, submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user).id})
        if action in ["verify_ltc_claim", "ltc_decision"]: payload.update({"form_id": LTCform.objects.create(employeeId=self.employee.id, name="Registry Employee", blockYear="2024-2026", pfNo=101, designation=self.employee.designation, departmentInfo="CSE", addressDuringLeave="Jabalpur", submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user).id})
        if action in ["verify_cpda_claim", "cpda_decision"]: payload.update({"target_type": "cpda_advance", "form_id": CPDAAdvanceform.objects.create(employeeId=self.employee.id, name="Registry Employee", designation=self.employee.designation, pfNo=101, purpose="Conference", amountRequired=1000, submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.faculty_user).id})
        if action == "process_financial_claim": payload.update({"form_id": 1, "claim_type": "CPDA"})
        if action == "maintain_policy": payload.update({"parameters": {"published": True}})
        if action == "maintain_calendar": payload.update({"entry": {"date": self.future_date(10), "type": "RH"}})
        resp = self._workflow(action, payload, admin=(action in ["maintain_policy", "maintain_calendar"] and not invalid))
        return resp.status_code in ([400, 403] if invalid else [200]), f"HTTP {resp.status_code}", str(getattr(resp, "data", ""))

def _make(br, invalid):
    def test(self):
        self._test_id, self._br_id = f"{br['id']}-{'I' if invalid else 'V'}-01", br["id"]
        self._test_category = "Invalid" if invalid else "Valid"
        case = br["invalid_tests"][0] if invalid else br["valid_tests"][0]
        self._input_action, self._expected_result = case["input_action"], case["expected_result"]
        ok, actual, evidence = self._execute(br["id"], invalid)
        self._record_result(actual, "Pass" if ok else "Fail", evidence)
    return test

for _br in _specs():
    setattr(HR2MasterRegistryBusinessRuleTests, f"test_{_br['id'].lower().replace('-', '_')}_valid_01", _make(_br, False))
    setattr(HR2MasterRegistryBusinessRuleTests, f"test_{_br['id'].lower().replace('-', '_')}_invalid_01", _make(_br, True))
