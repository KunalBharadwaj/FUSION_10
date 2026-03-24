from django.core.exceptions import PermissionDenied, ValidationError
from datetime import datetime, date
from applications.globals.models import HoldsDesignation, ExtraInfo
from .models import Constants, LeaveForm, LeaveBalance, LeaveClaim, LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform, Employee
from .selectors import get_employee_by_user, get_leave_balance, get_leave_form_by_id

class HRAccessDenied(PermissionDenied):
    pass

class InsufficientBalance(ValidationError):
    pass

class ProfileIncomplete(ValidationError):
    pass

class AppraisalWindowClosed(ValidationError):
    pass

class BlockYearInvalid(ValidationError):
    pass

def check_hr_access(user):
    if not user.is_authenticated:
         raise HRAccessDenied("User not authenticated.")
    emp = get_employee_by_user(user)
    if not emp:
        raise HRAccessDenied("Employee profile not found.")

def submit_leave_form(user, data):
    emp = get_employee_by_user(user)
    if not emp:
         raise ValidationError("Employee profile required to submit leave.")
    
    start_date = data.get('leaveStartDate')
    end_date = data.get('leaveEndDate')
    if start_date and end_date and start_date > end_date:
        raise ValidationError("End date cannot be before start date.")
    
    leave_type = data.get('natureOfLeave', 'casual_leave') 
    
    form = LeaveForm.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        submissionDate=date.today(),
        pfNo=data.get('pfNo'),
        departmentInfo=data.get('departmentInfo'),
        natureOfLeave=leave_type,
        leaveStartDate=start_date,
        leaveEndDate=end_date,
        purposeOfLeave=data.get('purposeOfLeave'),
        addressDuringLeave=data.get('addressDuringLeave'),
        academicResponsibility=data.get('academicResponsibility'),
        addministrativeResponsibiltyAssigned=data.get('addministrativeResponsibiltyAssigned'),
        status=Constants.Status.PENDING,
        created_by=user
    )
    return form

def handle_leave_file(form_id, user, action, remarks, forward_to=None, forward_designation=None):
    form = get_leave_form_by_id(form_id)
    if not form:
        raise ValidationError("Form not found.")
    
    if action == 'FORWARD':
        form.status = Constants.Status.FORWARDED
        if forward_designation:
            form.addministrativeResponsibiltyAssigned = forward_designation
    elif action == 'ACCEPT':
        form.status = Constants.Status.APPROVED
        form.approved = True
        form.approvedDate = date.today()
        form.approved_by = user
    elif action == 'REJECT':
        form.status = Constants.Status.REJECTED
        
    form.save()
    return form

def handle_academic_responsibility(form_id, user, action):
    form = get_leave_form_by_id(form_id)
    if not form:
         raise ValidationError("Form not found.")
    return form

def handle_admin_responsibility(form_id, user, action):
    form = get_leave_form_by_id(form_id)
    if not form:
         raise ValidationError("Form not found.")
    return form

def submit_ltc_form(user, data):
    emp = get_employee_by_user(user)
    if not emp:
         raise ProfileIncomplete("Employee profile required.")
    
    form = LTCform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        departmentInfo=data.get('departmentInfo', ''),
        blockYear=data.get('blockYear', ''),
        pfNo=data.get('pfNo', 0),
        basicPaySalary=data.get('basicPaySalary', 0),
        submissionDate=date.today(),
        status=Constants.Status.PENDING,
        created_by=user
    )
    return form

def submit_cpda_advance(user, data):
    emp = get_employee_by_user(user)
    if not emp:
        raise ProfileIncomplete("Employee profile required.")
        
    form = CPDAAdvanceform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        pfNo=data.get('pfNo', 0),
        purpose=data.get('purpose', ''),
        amountRequired=data.get('amountRequired', 0),
        submissionDate=date.today(),
        status=Constants.Status.PENDING,
        created_by=user
    )
    return form

def submit_cpda_reimbursement(user, data):
    emp = get_employee_by_user(user)
    form = CPDAReimbursementform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        pfNo=data.get('pfNo', 0),
        advanceTaken=data.get('advanceTaken', 0),
        purpose=data.get('purpose', ''),
        status=Constants.Status.PENDING,
        created_by=user
    )
    return form

def submit_appraisal(user, data):
    emp = get_employee_by_user(user)
    today = date.today()
    if not (today.month == 1 or today.month == 2):
        raise AppraisalWindowClosed("Submissions are only allowed between Jan 1 - Feb 28.")
        
    form = Appraisalform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        submissionDate=today,
        status=Constants.Status.PENDING,
        created_by=user,
        year=date(today.year, 1, 1)
    )
    return form

def admin_update_leave_balance(admin_user, emp_id, data):
    if not HoldsDesignation.objects.filter(user=admin_user, designation__name='HR_Admin').exists() and not admin_user.is_superuser:
         pass 
    
    emp = Employee.objects.filter(id=emp_id).first()
    if not emp:
        raise ValidationError("Employee not found.")
        
    balance, _ = LeaveBalance.objects.get_or_create(employeeId=emp.extra_info)
    
    if 'casualLeave' in data: balance.casualLeave = data['casualLeave']
    if 'earnedLeave' in data: balance.earnedLeave = data['earnedLeave']
    if 'restrictedHoliday' in data: balance.restrictedHoliday = data['restrictedHoliday']
    balance.save()
    return balance

def archive_form(form, user):
    form.status = Constants.Status.ARCHIVED
    form.save()
    return form
