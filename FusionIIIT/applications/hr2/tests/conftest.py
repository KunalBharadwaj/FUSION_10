"""
Base test configuration for HR2 module specification-based testing.
All test classes inherit from BaseModuleTestCase.

Architecture:
- UCTestBase   → for Use Case tests
- BRTestBase   → for Business Rule tests
- WFTestBase   → for Workflow tests (with step tracking)
"""
import csv
import os
from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from applications.globals.models import ExtraInfo, Designation, HoldsDesignation
from applications.hr2.models import (
    Constants, Employee, LeaveBalance, LeaveForm, LTCform,
    CPDAAdvanceform, CPDAReimbursementform, Appraisalform, LeavePerYear
)

# ─── Shared result store (populated during tests, consumed by runner) ─────────
_TEST_RESULTS = []


class BaseModuleTestCase(TestCase):
    """
    Base class that creates all shared test data once per class.
    Subclasses must call super().setUpTestData() if they override it.
    """

    @classmethod
    def setUpTestData(cls):
        # ── Faculty employee ──────────────────────────────────────────────────
        cls.faculty_user = User.objects.create_user(
            username='faculty01', password='testpass123',
            first_name='Ratan', last_name='Kumar'
        )
        cls.faculty_extra = ExtraInfo.objects.create(
            id='faculty01', user=cls.faculty_user, user_type='faculty'
        )
        cls.faculty_desig = Designation.objects.create(name='Assistant_Professor')
        HoldsDesignation.objects.create(
            user=cls.faculty_user,
            designation=cls.faculty_desig,
            working=cls.faculty_user
        )
        cls.employee = Employee.objects.create(
            extra_info=cls.faculty_extra,
            employee_type=Constants.EmployeeType.FACULTY,
            designation='Assistant_Professor',
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.O_POS
        )

        # ── Staff employee ────────────────────────────────────────────────────
        cls.staff_user = User.objects.create_user(
            username='staff01', password='testpass123',
            first_name='Priya', last_name='Sharma'
        )
        cls.staff_extra = ExtraInfo.objects.create(
            id='staff01', user=cls.staff_user, user_type='staff'
        )
        cls.staff_desig = Designation.objects.create(name='Staff_Member')
        HoldsDesignation.objects.create(
            user=cls.staff_user,
            designation=cls.staff_desig,
            working=cls.staff_user
        )
        cls.staff_employee = Employee.objects.create(
            extra_info=cls.staff_extra,
            employee_type=Constants.EmployeeType.STAFF,
            designation='Staff_Member',
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.A_POS
        )

        # ── HR Admin ─────────────────────────────────────────────────────────
        cls.admin_user = User.objects.create_user(
            username='hradmin01', password='testpass123',
            first_name='HR', last_name='Admin'
        )
        cls.admin_extra = ExtraInfo.objects.create(
            id='hradmin01', user=cls.admin_user, user_type='staff'
        )
        cls.admin_desig = Designation.objects.create(name='HR_Admin')
        HoldsDesignation.objects.create(
            user=cls.admin_user,
            designation=cls.admin_desig,
            working=cls.admin_user
        )
        Employee.objects.create(
            extra_info=cls.admin_extra,
            employee_type=Constants.EmployeeType.STAFF,
            designation='HR_Admin',
            category=Constants.Category.GENERAL,
            blood_group=Constants.BloodGroup.B_POS
        )

        # ── Unauthenticated client placeholder ────────────────────────────────
        # ── Leave balance for faculty ─────────────────────────────────────────
        cls.leave_balance = LeaveBalance.objects.create(
            employeeId=cls.faculty_extra,
            casualLeave=8,
            earnedLeave=15,
            vacationLeave=60,
            restrictedHoliday=2,
            commutedLeave=20,
            specialCasualLeave=15,
        )

        # ── Leave balance for staff ───────────────────────────────────────────
        cls.staff_balance = LeaveBalance.objects.create(
            employeeId=cls.staff_extra,
            casualLeave=8,
            earnedLeave=15,
            vacationLeave=0,
            restrictedHoliday=2,
            commutedLeave=20,
            specialCasualLeave=15,
        )

        # ── LeavePerYear default values ───────────────────────────────────────
        LeavePerYear.objects.get_or_create(year=2026)

    def setUp(self):
        """Create a fresh API client per test."""
        self.client = APIClient()

    # ── Login helpers ─────────────────────────────────────────────────────────
    def login_as_faculty(self):
        self.client.force_authenticate(user=self.faculty_user)

    def login_as_staff(self):
        self.client.force_authenticate(user=self.staff_user)

    def login_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

    def logout(self):
        self.client.force_authenticate(user=None)

    # ── HTTP helper shortcuts ─────────────────────────────────────────────────
    def api_get(self, url, expected_status=200):
        response = self.client.get(url)
        if expected_status is not None:
            self.assertEqual(response.status_code, expected_status)
        return response

    def api_post(self, url, data=None, expected_status=None, format='json'):
        response = self.client.post(url, data or {}, format=format)
        if expected_status is not None:
            self.assertEqual(response.status_code, expected_status)
        return response

    # ── Date helpers ──────────────────────────────────────────────────────────
    def future_date(self, days=5):
        return (date.today() + timedelta(days=days)).isoformat()

    def past_date(self, days=3):
        return (date.today() - timedelta(days=days)).isoformat()

    def today(self):
        return date.today().isoformat()

    # ── DB assertion helpers ──────────────────────────────────────────────────
    def assert_object_exists(self, model, **kwargs):
        exists = model.objects.filter(**kwargs).exists()
        self.assertTrue(exists, f"{model.__name__} not found with {kwargs}")

    def assert_object_not_exists(self, model, **kwargs):
        exists = model.objects.filter(**kwargs).exists()
        self.assertFalse(exists, f"{model.__name__} unexpectedly found with {kwargs}")


# ─── UC Test Base ─────────────────────────────────────────────────────────────
class UCTestBase(BaseModuleTestCase):
    """Base for Use-Case tests. Sets default metadata; override in each test."""

    def setUp(self):
        super().setUp()
        # Metadata (overridden per test)
        self._test_id = 'UC-?-?-?'
        self._uc_id = '?'
        self._test_category = 'Happy Path'
        self._scenario = ''
        self._preconditions = ''
        self._input_action = ''
        self._expected_result = ''
        # Result fields (populated by _record_result)
        self._actual_result = ''
        self._status = 'Fail'
        self._evidence = ''

    def _record_result(self, actual_result, status, evidence=''):
        self._actual_result = actual_result
        self._status = status
        self._evidence = evidence
        _TEST_RESULTS.append({
            'test_id': self._test_id,
            'source_type': 'UC',
            'source_id': self._uc_id,
            'test_category': self._test_category,
            'scenario': self._scenario,
            'preconditions': self._preconditions,
            'input_action': self._input_action,
            'expected_result': self._expected_result,
            'actual_result': actual_result,
            'status': status,
            'evidence': evidence,
            'tester': 'GPT-5.3 Codex',
        })


# ─── BR Test Base ─────────────────────────────────────────────────────────────
class BRTestBase(BaseModuleTestCase):
    """Base for Business-Rule tests."""

    def setUp(self):
        super().setUp()
        self._test_id = 'BR-?-?-?'
        self._br_id = '?'
        self._test_category = 'Valid'
        self._input_action = ''
        self._expected_result = ''
        self._actual_result = ''
        self._status = 'Fail'
        self._evidence = ''

    def _record_result(self, actual_result, status, evidence=''):
        self._actual_result = actual_result
        self._status = status
        self._evidence = evidence
        _TEST_RESULTS.append({
            'test_id': self._test_id,
            'source_type': 'BR',
            'source_id': self._br_id,
            'test_category': self._test_category,
            'scenario': '',
            'preconditions': '',
            'input_action': self._input_action,
            'expected_result': self._expected_result,
            'actual_result': actual_result,
            'status': status,
            'evidence': evidence,
            'tester': 'GPT-5.3 Codex',
        })


# ─── WF Test Base ─────────────────────────────────────────────────────────────
class WFTestBase(BaseModuleTestCase):
    """Base for Workflow tests with step tracking."""

    def setUp(self):
        super().setUp()
        self._test_id = 'WF-?-?-?'
        self._wf_id = '?'
        self._test_category = 'End-to-End'
        self._scenario = ''
        self._expected_final_state = ''
        self._actual_result = ''
        self._status = 'Fail'
        self._evidence = ''
        self._steps = []

    def _add_step(self, step_num, description, expected, actual, passed):
        self._steps.append({
            'step': step_num,
            'description': description,
            'expected': expected,
            'actual': actual,
            'passed': passed,
        })

    def _all_steps_passed(self):
        return all(s['passed'] for s in self._steps)

    def _record_result(self, actual_result, status, evidence=''):
        self._actual_result = actual_result
        self._status = status
        steps_summary = ' | '.join(
            f"Step{s['step']}({'OK' if s['passed'] else 'FAIL'}): {s['description']}"
            for s in self._steps
        )
        self._evidence = evidence or steps_summary
        _TEST_RESULTS.append({
            'test_id': self._test_id,
            'source_type': 'WF',
            'source_id': self._wf_id,
            'test_category': self._test_category,
            'scenario': self._scenario,
            'preconditions': '',
            'input_action': '',
            'expected_result': self._expected_final_state,
            'actual_result': actual_result,
            'status': status,
            'evidence': self._evidence,
            'tester': 'GPT-5.3 Codex',
        })
