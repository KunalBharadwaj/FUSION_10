import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from applications.hr2.models import Employee, Constants, LeaveForm
from applications.globals.models import ExtraInfo, Designation
from applications.hr2.services import submit_leave_form, HRAccessDenied, ValidationError

class HR2ModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.extra_info = ExtraInfo.objects.create(id='testuser', user=self.user)
        self.employee = Employee.objects.create(
            extra_info=self.extra_info, 
            employee_type=Constants.EmployeeType.FACULTY,
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS
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

    def test_submit_leave_form_date_inversion(self):
        data = {
            'leaveStartDate': '2026-04-05',
            'leaveEndDate': '2026-04-01',
        }
        with self.assertRaises(ValidationError):
            submit_leave_form(self.user, data)
