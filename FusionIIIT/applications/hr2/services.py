from django.core.exceptions import PermissionDenied, ValidationError
from datetime import datetime, date
from applications.globals.models import HoldsDesignation, ExtraInfo
from .models import Constants, LeaveForm, LeaveBalance, LeaveClaim, LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform, Employee
from .selectors import get_employee_by_user, get_leave_balance, get_leave_form_by_id

class LeaveTypeNotEligible(ValidationError):
    pass

class LeaveOverlapError(ValidationError):
    pass

class InvalidStatusTransition(ValidationError):
    pass

def validate_status_transition(current_status, new_status):
    """Validate status transitions follow allowed paths."""
    allowed_transitions = {
        Constants.Status.PENDING: [Constants.Status.FORWARDED, Constants.Status.REJECTED],
        Constants.Status.FORWARDED: [Constants.Status.APPROVED, Constants.Status.REJECTED],
        Constants.Status.APPROVED: [],  # Final state
        Constants.Status.REJECTED: [Constants.Status.PENDING],  # Allow rework
        Constants.Status.ARCHIVED: [],
    }
    
    if new_status not in allowed_transitions.get(current_status, []):
        raise InvalidStatusTransition(f"Invalid transition from {current_status} to {new_status}.")

def validate_file_attachment(file):
    """Validate uploaded file for type, size, and safety."""
    if not file:
        return
    
    # Check file size (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise FileValidationError("File size exceeds 5MB limit.")
    
    # Check file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        raise FileValidationError("Invalid file type. Only PDF, JPG, PNG allowed.")
    
    # Basic extension check
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    filename = file.name.lower()
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise FileValidationError("Invalid file extension.")

def check_leave_overlap(emp, start_date, end_date):
    """Check if the requested leave overlaps with existing approved or pending leaves."""
    overlapping_leaves = LeaveForm.objects.filter(
        employeeId=emp.id,
        status__in=[Constants.Status.PENDING, Constants.Status.APPROVED],
        leaveStartDate__lte=end_date,
        leaveEndDate__gte=start_date
    )
    if overlapping_leaves.exists():
        raise LeaveOverlapError("Leave request overlaps with existing leave(s).")

def check_leave_type_eligibility(emp, leave_type, balance):
    """Check if employee is eligible for the leave type based on role and balance."""
    user_type = emp.extra_info.user_type
    gender = emp.extra_info.user_gender if hasattr(emp.extra_info, 'user_gender') else None
    
    # Check role-based restrictions
    if leave_type == 'vacation_leave' and user_type != 'faculty':
        raise LeaveTypeNotEligible("Vacation Leave is only for Faculty.")
    
    if leave_type == 'maternity_leave' and gender != 'F':
        raise LeaveTypeNotEligible("Maternity Leave is only for Female employees.")
    
    if leave_type == 'paternity_leave' and gender != 'M':
        raise LeaveTypeNotEligible("Paternity Leave is only for Male employees.")
    
    # Check balance
    leave_balance_map = {
        'casual_leave': balance.casualLeave if balance else 0,
        'earned_leave': balance.earnedLeave if balance else 0,
        'restricted_holiday': balance.restrictedHoliday if balance else 0,
        'vacation_leave': balance.vacationLeave if balance else 0,
        'commuted_leave': balance.commutedLeave if balance else 0,
        'special_casual_leave': balance.specialCasualLeave if balance else 0,
    }
    
    required_balance = leave_balance_map.get(leave_type, 0)
    if required_balance <= 0:
        raise LeaveTypeNotEligible(f"Insufficient balance for {leave_type}.")

def check_cpda_advance_limit(emp, requested_amount):
    """Check if CPDA advance amount exceeds grade-wise limit."""
    # Map category to grade limits (example values)
    grade_limits = {
        'GENERAL': 50000,
        'OBC': 50000,
        'SC': 50000,
        'ST': 50000,
        'PWD': 50000,
    }
    
    category = emp.category
    annual_limit = grade_limits.get(category, 50000)
    
    # Check utilized amount (simplified - in real implementation, sum previous advances)
    utilized = 0  # TODO: Calculate from previous CPDA advances
    
    remaining_limit = annual_limit - utilized
    if requested_amount > remaining_limit:
        raise CPDAExceedsLimit(f"Requested amount exceeds grade limit. Remaining: {remaining_limit}")

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
    
    # Get leave balance
    balance, _ = get_leave_balance(emp)
    
    # Check leave type eligibility
    check_leave_type_eligibility(emp, leave_type, balance)
    
    # Check for leave overlap
    if start_date and end_date:
        check_leave_overlap(emp, start_date, end_date)
    
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
    
    new_status = None
    if action == 'FORWARD':
        new_status = Constants.Status.FORWARDED
        if forward_designation:
            form.addministrativeResponsibiltyAssigned = forward_designation
    elif action == 'ACCEPT':
        new_status = Constants.Status.APPROVED
        form.approved = True
        form.approvedDate = date.today()
        form.approved_by = user
    elif action == 'REJECT':
        new_status = Constants.Status.REJECTED
        if not remarks or len(remarks.strip()) < 10:
            raise ValidationError("Rejection remarks must be at least 10 characters.")
    
    if new_status:
        validate_status_transition(form.status, new_status)
        form.status = new_status
        
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
    
    requested_amount = data.get('amountRequired', 0)
    check_cpda_advance_limit(emp, requested_amount)
        
    form = CPDAAdvanceform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        pfNo=data.get('pfNo', 0),
        purpose=data.get('purpose', ''),
        amountRequired=requested_amount,
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
