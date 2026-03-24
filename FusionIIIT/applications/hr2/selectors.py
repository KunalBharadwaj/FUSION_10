from datetime import datetime, timedelta
from django.db.models import Q
from .models import (
    Employee, LeaveBalance, LeavePerYear, LeaveForm, 
    LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform
)
from applications.globals.models import HoldsDesignation

def get_employee_by_user(user):
    try:
        return Employee.objects.get(extra_info__user=user)
    except Employee.DoesNotExist:
        return None

def get_leave_balance(employee):
    leave_per_year = LeavePerYear.objects.last() 
    if not leave_per_year:
        leave_per_year = LeavePerYear.objects.create()
    balance, created = LeaveBalance.objects.get_or_create(employeeId=employee.extra_info)
    return balance, leave_per_year

def get_leave_forms(employee, from_date=None):
    if not from_date:
        from_date = datetime.now() - timedelta(days=365)
    return LeaveForm.objects.filter(employeeId=employee.id, submissionDate__gte=from_date)

def get_leave_form_by_id(form_id):
    try:
        return LeaveForm.objects.get(id=form_id)
    except LeaveForm.DoesNotExist:
        return None

def get_leave_inbox(user):
    designations = [hd.designation.name for hd in HoldsDesignation.objects.filter(user=user)]
    return LeaveForm.objects.filter(status='PENDING', addministrativeResponsibiltyAssigned__in=designations)

def get_ltc_forms(employee):
    return LTCform.objects.filter(employeeId=employee.id)

def get_cpda_advance_forms(employee):
    return CPDAAdvanceform.objects.filter(employeeId=employee.id)

def get_cpda_reimbursement_forms(employee):
    return CPDAReimbursementform.objects.filter(employeeId=employee.id)

def get_appraisal_forms(employee):
    return Appraisalform.objects.filter(employeeId=employee.id)

def get_all_employee_balances():
    return LeaveBalance.objects.all()

def get_designations_for_user(user):
    return HoldsDesignation.objects.filter(user=user)

def search_employees(query):
    return Employee.objects.filter(
        Q(extra_info__user__first_name__icontains=query) | Q(extra_info__user__username__icontains=query)
    )
