from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from applications.hr2.models import Employee, Constants, LeaveForm, LeaveBalance, LeavePerYear, LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform
from applications.globals.models import ExtraInfo, Designation, HoldsDesignation
from applications.hr2.selectors import (
    get_employee_by_user, get_leave_balance, get_leave_forms, get_leave_form_by_id,
    get_leave_inbox, get_ltc_forms, get_cpda_advance_forms, get_cpda_reimbursement_forms,
    get_appraisal_forms, search_employees
)

class SelectorsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testemp', password='password', first_name='Test', last_name='Employee')
        self.extra_info = ExtraInfo.objects.create(id='testemp', user=self.user, user_type='faculty')
        self.designation = Designation.objects.create(name='Assistant Professor')
        HoldsDesignation.objects.create(user=self.user, designation=self.designation, working=self.user)
        self.employee = Employee.objects.create(
            extra_info=self.extra_info,
            employee_type=Constants.EmployeeType.FACULTY,
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS,
            designation='Assistant Professor'
        )

    def test_get_employee_by_user(self):
        emp = get_employee_by_user(self.user)
        self.assertIsNotNone(emp)
        self.assertEqual(emp.id, self.employee.id)

    def test_get_employee_by_user_not_found(self):
        other_user = User.objects.create_user(username='other', password='password')
        emp = get_employee_by_user(other_user)
        self.assertIsNone(emp)

    def test_get_leave_balance(self):
        balance, leave_per_year = get_leave_balance(self.employee)
        self.assertIsNotNone(balance)
        self.assertIsNotNone(leave_per_year)
        self.assertEqual(balance.employeeId, self.extra_info)

    def test_get_leave_forms(self):
        LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        forms = get_leave_forms(self.employee)
        self.assertEqual(forms.count(), 1)

    def test_get_leave_form_by_id(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        fetched = get_leave_form_by_id(form.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, form.id)

    def test_get_leave_form_by_id_not_found(self):
        fetched = get_leave_form_by_id(999999)
        self.assertIsNone(fetched)

    def test_get_leave_inbox(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            addministrativeResponsibiltyAssigned=self.user.username,
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        inbox = get_leave_inbox(self.user)
        self.assertEqual(inbox.count(), 1)
        self.assertEqual(inbox.first().id, form.id)

    def test_get_leave_inbox_includes_forwarded_username_route(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            addministrativeResponsibiltyAssigned=self.user.username,
            submissionDate=date.today(), status=Constants.Status.FORWARDED, created_by=self.user
        )
        inbox = get_leave_inbox(self.user)
        self.assertEqual(inbox.count(), 1)
        self.assertEqual(inbox.first().id, form.id)

    def test_get_ltc_forms(self):
        form = LTCform.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            blockYear='2024-2026', pfNo=123, departmentInfo='CSE',
            submissionDate=date.today(),
            status=Constants.Status.PENDING, created_by=self.user
        )
        forms = get_ltc_forms(self.employee)
        self.assertEqual(forms.count(), 1)
        self.assertEqual(forms.first().id, form.id)

    def test_get_cpda_advance_forms(self):
        form = CPDAAdvanceform.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        forms = get_cpda_advance_forms(self.employee)
        self.assertEqual(forms.count(), 1)

    def test_get_cpda_reimbursement_forms(self):
        form = CPDAReimbursementform.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            pfNo=123, advanceTaken=5000, purpose='Conference reimbursement',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        forms = get_cpda_reimbursement_forms(self.employee)
        self.assertEqual(forms.count(), 1)

    def test_get_appraisal_forms(self):
        form = Appraisalform.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(),
            status=Constants.Status.PENDING, created_by=self.user
        )
        forms = get_appraisal_forms(self.employee)
        self.assertEqual(forms.count(), 1)

    def test_search_employees(self):
        results = search_employees('Test')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().id, self.employee.id)
