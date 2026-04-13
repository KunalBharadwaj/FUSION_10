from datetime import date, timedelta
from unittest.mock import patch
from .conftest import UCTestBase
from applications.hr2.models import Constants, LeaveForm, LTCform, CPDAAdvanceform, Appraisalform
from applications.hr2.services import submit_appraisal

WORKFLOW_URL = "/hr2/api/workflow_action/"
UC_ACTIONS = {
    "HR-UC-002": "nominate_substitute", "HR-UC-003": "respond_substitute",
    "HR-UC-004": "modify_request", "HR-UC-005": "withdraw_request",
    "HR-UC-006": "acknowledge_withdrawal", "HR-UC-007": "request_cancellation",
    "HR-UC-008": "submit_extension", "HR-UC-009": "submit_resumption",
    "HR-UC-010": "verify_resumption", "HR-UC-013": "review_appraisal",
    "HR-UC-014": "appraisal_decision", "HR-UC-016": "verify_ltc_claim",
    "HR-UC-017": "ltc_decision", "HR-UC-019": "process_financial_claim",
    "HR-UC-020": "hod_decision", "HR-UC-021": "sanctioning_decision",
    "HR-UC-022": "run_year_end_leave_closure", "HR-UC-023": "run_sla",
    "HR-UC-024": "maintain_policy", "HR-UC-025": "maintain_calendar",
}

def _specs():
    import os, yaml
    with open(os.path.join(os.path.dirname(__file__), "specs", "use_cases.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)["use_cases"]

class HR2MasterRegistryUseCaseTests(UCTestBase):
    def _leave(self, status=Constants.Status.PENDING, start=5, end=6):
        return LeaveForm.objects.create(employeeId=self.employee.id, name="Registry Employee",
            designation=self.employee.designation, submissionDate=date.today(), pfNo=101,
            departmentInfo="CSE", natureOfLeave="casual_leave",
            leaveStartDate=date.today() + timedelta(days=start),
            leaveEndDate=date.today() + timedelta(days=end),
            purposeOfLeave="Registry test", addressDuringLeave="Jabalpur",
            status=status, created_by=self.faculty_user)

    def _appraisal(self, status=Constants.Status.PENDING):
        return Appraisalform.objects.create(employeeId=self.employee.id, name="Registry Employee",
            designation=self.employee.designation, submissionDate=date.today(),
            status=status, created_by=self.faculty_user)

    def _ltc(self, status=Constants.Status.PENDING):
        return LTCform.objects.create(employeeId=self.employee.id, name="Registry Employee",
            blockYear="2024-2026", pfNo=101, designation=self.employee.designation,
            departmentInfo="CSE", addressDuringLeave="Jabalpur", submissionDate=date.today(),
            status=status, created_by=self.faculty_user)

    def _cpda(self, status=Constants.Status.PENDING):
        return CPDAAdvanceform.objects.create(employeeId=self.employee.id, name="Registry Employee",
            designation=self.employee.designation, pfNo=101, purpose="Conference",
            amountRequired=1000, submissionDate=date.today(), status=status,
            created_by=self.faculty_user)

    def _workflow(self, action, payload=None, admin=False):
        self.login_as_admin() if admin else self.login_as_faculty()
        return self.api_post(WORKFLOW_URL, {"action": action, "payload": payload or {}}, expected_status=None)

    def _payload(self, action, category):
        invalid = category == "exception_paths"
        if action == "nominate_substitute":
            return {"substitute_username": self.faculty_user.username if invalid else self.staff_user.username}
        if action == "respond_substitute":
            return {"decision": "BAD" if invalid else ("DECLINE" if category == "alternate_paths" else "ACCEPT")}
        if action in ["modify_request", "withdraw_request", "acknowledge_withdrawal", "request_cancellation",
                      "submit_extension", "submit_resumption", "verify_resumption", "hod_decision", "sanctioning_decision"]:
            status = Constants.Status.APPROVED if action in ["request_cancellation", "submit_extension", "submit_resumption", "verify_resumption"] else Constants.Status.PENDING
            if invalid and action in ["modify_request", "withdraw_request"]:
                status = Constants.Status.APPROVED
            start, end = (-20, -15) if invalid and action in ["request_cancellation", "submit_resumption"] else ((-1, 1) if action in ["submit_extension", "submit_resumption"] else (5, 6))
            form = self._leave(status=status, start=start, end=end)
            payload = {"form_id": 999999 if invalid and action in ["acknowledge_withdrawal", "verify_resumption"] else form.id,
                       "decision": "REJECT" if category == "alternate_paths" else "APPROVE",
                       "remarks": "Rejected with sufficient detail",
                       "new_end_date": self.future_date(1 if invalid and action == "submit_extension" else 5),
                       "resumption_date": self.today()}
            if invalid and action in ["hod_decision", "sanctioning_decision"]:
                payload["invalid"] = True
            return payload
        if action in ["review_appraisal", "appraisal_decision"]:
            form = self._appraisal(Constants.Status.FORWARDED if action == "appraisal_decision" else Constants.Status.PENDING)
            return {"form_id": 999999 if invalid and action == "review_appraisal" else form.id,
                    "decision": "BAD" if invalid else ("REJECT" if category == "alternate_paths" else "APPROVE")}
        if action in ["verify_ltc_claim", "ltc_decision"]:
            form = self._ltc(Constants.Status.FORWARDED if action == "ltc_decision" else Constants.Status.PENDING)
            return {"form_id": 999999 if invalid and action == "verify_ltc_claim" else form.id,
                    "decision": "BAD" if invalid else ("REJECT" if category == "alternate_paths" else "APPROVE")}
        if action == "process_financial_claim":
            return {"invalid": invalid, "form_id": self._ltc(Constants.Status.APPROVED).id, "claim_type": "CPDA" if category == "alternate_paths" else "LTC"}
        if action in ["run_year_end_leave_closure", "run_sla"]:
            return {"invalid": invalid, "assignee": self.staff_user.username}
        if action == "maintain_policy":
            return {"parameters": {"cancellation_window_days": 5}}
        if action == "maintain_calendar":
            return {"entry": {"date": self.future_date(10), "type": "RH"}}
        return {"invalid": invalid}

    def _execute(self, uc_id, category):
        if uc_id == "HR-UC-001":
            self.login_as_faculty()
            data = {"pfNo": 101, "departmentInfo": "CSE", "natureOfLeave": "casual_leave",
                    "leaveStartDate": self.future_date(8 if category == "exception_paths" else 5),
                    "leaveEndDate": self.future_date(2 if category == "exception_paths" else 6),
                    "purposeOfLeave": "Registry leave", "addressDuringLeave": "Delhi" if category == "alternate_paths" else "Jabalpur",
                    "outOfJabalpur": category == "alternate_paths"}
            resp = self.api_post("/hr2/api/submit_leave_form/", data, expected_status=None)
            return resp.status_code == (400 if category == "exception_paths" else 201), f"HTTP {resp.status_code}", str(resp.data)
        if uc_id == "HR-UC-011":
            if category == "exception_paths": self.logout()
            else: self.login_as_faculty()
            url = "/hr2/api/get_leave_requests/" if category == "alternate_paths" else "/hr2/api/get_leave_balance/"
            resp = self.api_get(url, expected_status=None)
            return resp.status_code in ([401, 403] if category == "exception_paths" else [200]), f"HTTP {resp.status_code}", str(getattr(resp, "data", ""))
        if uc_id == "HR-UC-012":
            if category == "alternate_paths":
                self.login_as_faculty(); self._appraisal(); resp = self.api_get("/hr2/api/appraisal/", expected_status=None)
                return resp.status_code == 200, f"HTTP {resp.status_code}", str(resp.data)
            import datetime
            class MockDate(datetime.date):
                @classmethod
                def today(cls): return cls(2026, 4 if category == "exception_paths" else 1, 15)
            try:
                with patch("applications.hr2.services.date", MockDate): submit_appraisal(self.faculty_user, {})
                return category != "exception_paths", "Appraisal created", "patched date"
            except Exception as exc:
                return category == "exception_paths", type(exc).__name__, str(exc)
        if uc_id == "HR-UC-015":
            self.login_as_faculty()
            data = {"blockYear": "2024-2026", "pfNo": 101, "basicPaySalary": 50000, "departmentInfo": "CSE", "addressDuringLeave": "Jabalpur"}
            if category != "happy_paths": data.update({"leaveRequired": True, "leaveStartDate": self.future_date(5), "leaveEndDate": self.future_date(2 if category == "exception_paths" else 6)})
            resp = self.api_post("/hr2/api/ltc/", data, expected_status=None)
            return resp.status_code == (400 if category == "exception_paths" else 201), f"HTTP {resp.status_code}", str(resp.data)
        if uc_id == "HR-UC-018":
            self.login_as_faculty()
            if category == "alternate_paths":
                resp = self.api_post("/hr2/api/cpdareim/", {"pfNo": 101, "advanceTaken": 500, "purpose": "Conference"}, expected_status=None)
            else:
                resp = self.api_post("/hr2/api/cpdaadv/", {"pfNo": 101, "amountRequired": 1000000 if category == "exception_paths" else 1000, "purpose": "Conference"}, expected_status=None)
            return resp.status_code == (400 if category == "exception_paths" else 201), f"HTTP {resp.status_code}", str(resp.data)
        action = UC_ACTIONS[uc_id]
        admin = action in ["maintain_policy", "maintain_calendar"] and category != "exception_paths"
        resp = self._workflow(action, self._payload(action, category), admin=admin)
        return resp.status_code in ([400, 403] if category == "exception_paths" else [200]), f"HTTP {resp.status_code}", str(getattr(resp, "data", ""))

def _make(uc, category, path):
    def test(self):
        suffix = {"happy_paths": "HP", "alternate_paths": "AP", "exception_paths": "EX"}[category]
        self._test_id, self._uc_id = f"{uc['id']}-{suffix}-01", uc["id"]
        self._test_category = {"happy_paths": "Happy Path", "alternate_paths": "Alternate Path", "exception_paths": "Exception"}[category]
        self._scenario, self._preconditions = path["scenario"], path["preconditions"]
        self._input_action, self._expected_result = path["input_action"], path["expected_result"]
        ok, actual, evidence = self._execute(uc["id"], category)
        self._record_result(actual, "Pass" if ok else "Fail", evidence)
    return test

for _uc in _specs():
    for _cat in ["happy_paths", "alternate_paths", "exception_paths"]:
        setattr(HR2MasterRegistryUseCaseTests, f"test_{_uc['id'].lower().replace('-', '_')}_{_cat}_01", _make(_uc, _cat, _uc[_cat][0]))
