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
    balance, created = LeaveBalance.objects.get_or_create(
        employeeId=employee.extra_info,
        defaults={
            'casualLeave': leave_per_year.casual_leave,
            'earnedLeave': leave_per_year.earned_leave,
            'restrictedHoliday': leave_per_year.restricted_holiday,
            'vacationLeave': leave_per_year.vacation_leave,
            'commutedLeave': leave_per_year.commuted_leave,
            'specialCasualLeave': leave_per_year.special_casual_leave,
        }
    )
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
    # The frontend form saves the substitute's username
    return LeaveForm.objects.filter(
        Q(status='PENDING') & 
        (Q(addministrativeResponsibiltyAssigned=user.username) | 
         Q(academicResponsibility=user.username))
    )

def get_ltc_forms(employee):
    return LTCform.objects.filter(employeeId=employee.id)

def get_cpda_advance_forms(employee):
    return CPDAAdvanceform.objects.filter(employeeId=employee.id)

def get_cpda_reimbursement_forms(employee):
    return CPDAReimbursementform.objects.filter(employeeId=employee.id)

def get_appraisal_forms(employee):
    return Appraisalform.objects.filter(employeeId=employee.id)

def _get_user_designations(user):
    """Return uppercase set of all designation names for a user."""
    return {
        str(hd.designation.name).strip().upper()
        for hd in HoldsDesignation.objects.filter(user=user).select_related("designation")
    }

def _has_any(desig_set, *names):
    """Check if any of the given names (case-insensitive) are in the designation set."""
    targets = {n.strip().upper() for n in names}
    return bool(desig_set & targets)

def get_ltc_inbox(user):
    desigs = _get_user_designations(user)
    inbox = []
    # HODs verify PENDING forms
    if _has_any(desigs, "HOD", "HEAD OF DEPARTMENT"):
        inbox.extend(list(LTCform.objects.filter(status='PENDING')))
    # Director / HR Admin give final approval on FORWARDED forms
    if _has_any(desigs, "DIRECTOR", "REGISTRAR", "HR ADMIN", "HR ADMINISTRATOR"):
        inbox.extend(list(LTCform.objects.filter(status='FORWARDED')))
    # Accountant processes financially-approved forms
    if _has_any(desigs, "ACCOUNTANT", "FINANCE"):
        inbox.extend(list(LTCform.objects.filter(status='APPROVED')))
    # Deduplicate preserving order
    seen = set()
    result = []
    for f in inbox:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f)
    return result

def get_cpda_advance_inbox(user):
    desigs = _get_user_designations(user)
    inbox = []
    if _has_any(desigs, "HOD", "HEAD OF DEPARTMENT"):
        inbox.extend(list(CPDAAdvanceform.objects.filter(status='PENDING')))
    if _has_any(desigs, "DIRECTOR", "REGISTRAR"):
        inbox.extend(list(CPDAAdvanceform.objects.filter(status='FORWARDED')))
    if _has_any(desigs, "ACCOUNTANT", "FINANCE"):
        inbox.extend(list(CPDAAdvanceform.objects.filter(status='APPROVED')))
    seen = set()
    result = []
    for f in inbox:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f)
    return result

def get_cpda_reimbursement_inbox(user):
    desigs = _get_user_designations(user)
    inbox = []
    if _has_any(desigs, "HOD", "HEAD OF DEPARTMENT"):
        inbox.extend(list(CPDAReimbursementform.objects.filter(status='PENDING')))
    if _has_any(desigs, "DIRECTOR", "REGISTRAR"):
        inbox.extend(list(CPDAReimbursementform.objects.filter(status='FORWARDED')))
    if _has_any(desigs, "ACCOUNTANT", "FINANCE"):
        inbox.extend(list(CPDAReimbursementform.objects.filter(status='APPROVED')))
    seen = set()
    result = []
    for f in inbox:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f)
    return result

def get_appraisal_inbox(user):
    desigs = _get_user_designations(user)
    inbox = []
    if _has_any(desigs, "HOD", "HEAD OF DEPARTMENT"):
        inbox.extend(list(Appraisalform.objects.filter(status='PENDING')))
    if _has_any(desigs, "HR ADMIN", "HR ADMINISTRATOR", "DIRECTOR"):
        inbox.extend(list(Appraisalform.objects.filter(status='FORWARDED')))
    seen = set()
    result = []
    for f in inbox:
        if f.id not in seen:
            seen.add(f.id)
            result.append(f)
    return result

def get_all_employee_balances():

    return LeaveBalance.objects.all()

def get_designations_for_user(user):
    return HoldsDesignation.objects.filter(user=user)

def search_employees(query):
    return Employee.objects.filter(
        Q(extra_info__user__first_name__icontains=query) | Q(extra_info__user__username__icontains=query)
    )
