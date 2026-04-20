from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from applications.hr2.models import Employee, Constants, LeaveForm, LeaveBalance, LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform
from applications.globals.models import ExtraInfo, Designation, HoldsDesignation
from applications.hr2.services import (
    submit_leave_form, handle_leave_file, submit_ltc_form, submit_cpda_advance,
    submit_cpda_reimbursement, submit_appraisal, admin_update_leave_balance,
    HRAccessDenied, ProfileIncomplete, AppraisalWindowClosed
)

class ServicesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testemp', password='password', first_name='Test', last_name='Employee')
        self.extra_info = ExtraInfo.objects.create(id='testemp', user=self.user, user_type='faculty')
        self.employee = Employee.objects.create(
            extra_info=self.extra_info,
            employee_type=Constants.EmployeeType.FACULTY,
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS,
            designation='Assistant Professor'
        )
        self.substitute_user = User.objects.create_user(
            username='hod1002', password='password', first_name='Anil', last_name='Kumar'
        )
        self.substitute_info = ExtraInfo.objects.create(
            id='hod1002', user=self.substitute_user, user_type='faculty'
        )
        self.substitute_employee = Employee.objects.create(
            extra_info=self.substitute_info,
            employee_type=Constants.EmployeeType.FACULTY,
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS,
            designation='Associate Professor'
        )
        self.forward_user = User.objects.create_user(
            username='director01', password='password', first_name='Director', last_name='User'
        )
        self.forward_info = ExtraInfo.objects.create(
            id='director01', user=self.forward_user, user_type='faculty'
        )
        self.forward_employee = Employee.objects.create(
            extra_info=self.forward_info,
            employee_type=Constants.EmployeeType.FACULTY,
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS,
            designation='Director'
        )

    def test_submit_leave_form_success(self):
        data = {
            'pfNo': 1234,
            'departmentInfo': 'CSE',
            'natureOfLeave': 'casual_leave',
            'leaveStartDate': '2026-04-01',
            'leaveEndDate': '2026-04-02',
            'purposeOfLeave': 'Personal',
        }
        form = submit_leave_form(self.user, data)
        self.assertEqual(form.status, Constants.Status.PENDING)
        self.assertEqual(form.created_by, self.user)
        self.assertEqual(form.employeeId, self.employee.id)

    def test_submit_leave_form_routes_to_selected_substitute(self):
        data = {
            'pfNo': 1234,
            'departmentInfo': 'CSE',
            'natureOfLeave': 'casual_leave',
            'leaveStartDate': '2026-04-01',
            'leaveEndDate': '2026-04-02',
            'purposeOfLeave': 'Personal',
            'academicResponsibility': self.substitute_user.username,
        }
        form = submit_leave_form(self.user, data)
        self.assertEqual(form.academicResponsibility, self.substitute_user.username)

    def test_submit_leave_form_rejects_self_substitute(self):
        data = {
            'pfNo': 1234,
            'departmentInfo': 'CSE',
            'natureOfLeave': 'casual_leave',
            'leaveStartDate': '2026-04-01',
            'leaveEndDate': '2026-04-02',
            'purposeOfLeave': 'Personal',
            'academicResponsibility': self.user.username,
        }
        with self.assertRaises(ValidationError):
            submit_leave_form(self.user, data)

    def test_submit_leave_form_invalid_dates(self):
        data = {
            'leaveStartDate': '2026-04-05',
            'leaveEndDate': '2026-04-01',
        }
        with self.assertRaises(ValidationError):
            submit_leave_form(self.user, data)

    def test_submit_leave_form_requires_address_when_out_of_jabalpur(self):
        data = {
            'pfNo': 1234,
            'departmentInfo': 'CSE',
            'natureOfLeave': 'casual_leave',
            'leaveStartDate': '2026-04-01',
            'leaveEndDate': '2026-04-02',
            'purposeOfLeave': 'Personal',
            'outOfJabalpur': True,
            'addressDuringLeave': '',
        }
        with self.assertRaises(ValidationError):
            submit_leave_form(self.user, data)

    def test_handle_leave_file_forward(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            academicResponsibility=self.substitute_user.username,
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        updated_form = handle_leave_file(
            form.id, self.substitute_user, 'FORWARD', 'Looks good',
            forward_to=self.forward_user.username,
        )
        self.assertEqual(updated_form.status, Constants.Status.FORWARDED)
        self.assertEqual(updated_form.addministrativeResponsibiltyAssigned, self.forward_user.username)
        self.assertIsNone(updated_form.academicResponsibility)

    def test_handle_leave_file_accept(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        updated_form = handle_leave_file(form.id, self.user, 'ACCEPT', 'Approved')
        self.assertEqual(updated_form.status, Constants.Status.APPROVED)
        self.assertTrue(updated_form.approved)
        self.assertEqual(updated_form.approved_by, self.user)
        self.assertEqual(updated_form.approvedDate, date.today())

    def test_handle_leave_file_reject(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        updated_form = handle_leave_file(form.id, self.user, 'REJECT', 'Denied after review')
        self.assertEqual(updated_form.status, Constants.Status.REJECTED)

    def test_handle_leave_file_reject_requires_meaningful_remarks(self):
        form = LeaveForm.objects.create(
            employeeId=self.employee.id, name='Test', designation='Assistant Professor',
            submissionDate=date.today(), status=Constants.Status.PENDING, created_by=self.user
        )
        with self.assertRaises(ValidationError):
            handle_leave_file(form.id, self.user, 'REJECT', 'Too short')

    def test_submit_ltc_form(self):
        data = {'blockYear': '2024-2026', 'pfNo': 123, 'basicPaySalary': 50000}
        form = submit_ltc_form(self.user, data)
        self.assertEqual(form.status, Constants.Status.PENDING)
        self.assertEqual(form.employeeId, self.employee.id)

    def test_submit_cpda_advance(self):
        data = {'pfNo': 123, 'purpose': 'Conference', 'amountRequired': 10000}
        form = submit_cpda_advance(self.user, data)
        self.assertEqual(form.status, Constants.Status.PENDING)
        self.assertEqual(form.amountRequired, 10000)

    def test_submit_cpda_reimbursement(self):
        data = {'pfNo': 123, 'advanceTaken': 5000, 'purpose': 'Conference'}
        form = submit_cpda_reimbursement(self.user, data)
        self.assertEqual(form.status, Constants.Status.PENDING)
        self.assertEqual(form.advanceTaken, 5000)

    def test_submit_appraisal_success(self):
        import datetime
        from unittest.mock import patch
        data = {}
        # Mock date.today() to be in January
        class MockDate(datetime.date):
            @classmethod
            def today(cls):
                return cls(2026, 1, 15)
                
        with patch('applications.hr2.services.date', MockDate):
            form = submit_appraisal(self.user, data)
            self.assertEqual(form.status, Constants.Status.PENDING)

    def test_submit_appraisal_closed_window(self):
        import datetime
        from unittest.mock import patch
        data = {}
        # Mock date.today() to be in May
        class MockDate(datetime.date):
            @classmethod
            def today(cls):
                return cls(2026, 5, 15)
                
        with patch('applications.hr2.services.date', MockDate):
            with self.assertRaises(AppraisalWindowClosed):
                submit_appraisal(self.user, data)

    def test_admin_update_leave_balance(self):
        # Create hr admin
        admin_user = User.objects.create_user(username='admin', password='password')
        hr_desig, _ = Designation.objects.get_or_create(name='HR_Admin')
        HoldsDesignation.objects.create(user=admin_user, designation=hr_desig, working=admin_user)
        
        data = {'casualLeave': 10, 'earnedLeave': 15, 'restrictedHoliday': 2}
        balance = admin_update_leave_balance(admin_user, self.employee.id, data)
        self.assertEqual(balance.casualLeave, 10)
        self.assertEqual(balance.earnedLeave, 15)
        self.assertEqual(balance.restrictedHoliday, 2)
