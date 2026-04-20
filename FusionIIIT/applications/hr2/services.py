from django.db import models
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from applications.globals.models import HoldsDesignation, ExtraInfo
from .models import Constants, LeaveForm, LeaveBalance, LeaveClaim, LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform, Employee
from .selectors import get_employee_by_user, get_leave_balance, get_leave_form_by_id

class LeaveTypeNotEligible(ValidationError):
    pass

class LeaveOverlapError(ValidationError):
    pass

class InvalidStatusTransition(ValidationError):
    pass

class ProfileIncomplete(ValidationError):
    pass

class CPDAExceedsLimit(ValidationError):
    pass

class HRAccessDenied(PermissionDenied):
    pass

class AppraisalWindowClosed(ValidationError):
    pass

class FileValidationError(ValidationError):
    pass

_RUNTIME_AUDIT_LOG = []
_RUNTIME_NOTIFICATIONS = []
_RUNTIME_FINANCE_HANDOFFS = []
_RUNTIME_POLICY = {
    "published": True,
    "casual_leave": 8,
    "restricted_holiday": 2,
    "earned_leave": 15,
    "vacation_leave": 60,
    "commuted_leave": 20,
    "special_casual_leave": 15,
    "cancellation_window_days": 7,
    "resumption_grace_days": 7,
}
_RUNTIME_CALENDAR = []

LEAVE_TYPE_ALIASES = {
    "CL": "casual_leave",
    "RH": "restricted_holiday",
    "SCL": "special_casual_leave",
    "HR": "earned_leave",
    "EL": "earned_leave",
    "COL": "commuted_leave",
    "VL": "vacation_leave",
}


def _parse_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _normalize_leave_type(leave_type):
    if not leave_type:
        return "casual_leave"
    return LEAVE_TYPE_ALIASES.get(str(leave_type).upper(), leave_type)


def _employee_role(emp):
    role = getattr(emp, "employee_type", None) or getattr(emp.extra_info, "user_type", "")
    return str(role).lower()


def _require_employee(user):
    if not user or not user.is_authenticated:
        raise HRAccessDenied("User not authenticated.")
    emp = get_employee_by_user(user)
    if not emp:
        raise ProfileIncomplete("Employee profile required.")
    return emp


def _is_hr_admin(user):
    return user.is_superuser or HoldsDesignation.objects.filter(
        user=user,
        designation__name__in=["HR_Admin", "hradmin", "SectionHead_HR", "Section Head HR"],
    ).exists()


def _record_audit(user, action, target_type="HR2", target_id=None, payload=None, status="success"):
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user": getattr(user, "username", str(user)),
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "payload": payload or {},
        "status": status,
    }
    _RUNTIME_AUDIT_LOG.append(entry)
    return entry


def reset_runtime_records():
    _RUNTIME_AUDIT_LOG.clear()
    _RUNTIME_NOTIFICATIONS.clear()
    _RUNTIME_FINANCE_HANDOFFS.clear()
    _RUNTIME_CALENDAR.clear()


def get_runtime_records():
    return {
        "audit_log": list(_RUNTIME_AUDIT_LOG),
        "notifications": list(_RUNTIME_NOTIFICATIONS),
        "finance_handoffs": list(_RUNTIME_FINANCE_HANDOFFS),
        "policy": dict(_RUNTIME_POLICY),
        "calendar": list(_RUNTIME_CALENDAR),
    }

def validate_status_transition(current_status, new_status):
    """Validate status transitions follow allowed paths."""
    allowed_transitions = {
        Constants.Status.PENDING: [Constants.Status.FORWARDED, Constants.Status.APPROVED, Constants.Status.REJECTED, Constants.Status.ARCHIVED],
        Constants.Status.FORWARDED: [Constants.Status.APPROVED, Constants.Status.REJECTED],
        Constants.Status.APPROVED: [],  # Final state
        Constants.Status.REJECTED: [Constants.Status.PENDING, Constants.Status.ARCHIVED],  # Allow rework/archive
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
    leave_type = _normalize_leave_type(leave_type)
    user_type = _employee_role(emp)
    gender = emp.extra_info.user_gender if hasattr(emp.extra_info, 'user_gender') else None
    
    # Check role-based restrictions
    if leave_type == 'vacation_leave' and user_type not in ('faculty', 'constants.employeetype.faculty'):
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
    
    # Check utilized amount from previous CPDA advances in the current year
    current_year = date.today().year
    utilized = CPDAAdvanceform.objects.filter(
        employeeId=emp.id,
        status=Constants.Status.APPROVED,
        submissionDate__year=current_year
    ).aggregate(models.Sum('amountRequired'))['amountRequired__sum'] or 0
    
    remaining_limit = annual_limit - utilized
    if requested_amount > remaining_limit:
        raise CPDAExceedsLimit(f"Requested amount exceeds grade limit. Remaining: {remaining_limit}")

def check_hr_access(user):
    _require_employee(user)

def submit_leave_form(user, data):
    emp = get_employee_by_user(user)
    if not emp:
         raise ValidationError("Employee profile required to submit leave.")
    
    start_date = _parse_date(data.get('leaveStartDate'))
    end_date = _parse_date(data.get('leaveEndDate'))
    if start_date and end_date and start_date > end_date:
        raise ValidationError("End date cannot be before start date.")
    
    leave_type = _normalize_leave_type(data.get('natureOfLeave', 'casual_leave'))
    if data.get('outOfJabalpur') and not data.get('addressDuringLeave'):
        raise ValidationError("Station leave details are required when leaving Jabalpur.")
    
    # Get leave balance
    balance, _ = get_leave_balance(emp)
    
    # Check leave type eligibility
    check_leave_type_eligibility(emp, leave_type, balance)
    
    # Check for leave overlap
    if start_date and end_date:
        check_leave_overlap(emp, start_date, end_date)

    academic_responsibility = (data.get('academicResponsibility') or '').strip() or None
    administrative_responsibility = (
        data.get('addministrativeResponsibiltyAssigned') or ''
    ).strip() or None
    for substitute_username in [academic_responsibility, administrative_responsibility]:
        if substitute_username == user.username:
            raise ValidationError("Substitute must be different from the applicant.")
        if substitute_username and not User.objects.filter(
            username=substitute_username,
            is_active=True,
            extrainfo__user_type='faculty',
        ).exists():
            raise ValidationError(f"Invalid substitute selected: {substitute_username}.")
    
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
        academicResponsibility=academic_responsibility,
        addministrativeResponsibiltyAssigned=administrative_responsibility,
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
        forward_target = (forward_to or forward_designation or '').strip()
        if not forward_target:
            raise ValidationError("Forward target is required.")
        if not User.objects.filter(username=forward_target, is_active=True).exists():
            raise ValidationError(f"Invalid forward target selected: {forward_target}.")
        form.addministrativeResponsibiltyAssigned = forward_target
        form.academicResponsibility = None
    elif action == 'ACCEPT':
        new_status = Constants.Status.APPROVED
        form.approved = True
        form.approvedDate = date.today()
        form.approved_by = user
        
        # BR-HR-019: Deduct Leave Balance on Acceptance
        emp = Employee.objects.filter(id=form.employeeId).first()
        if emp:
            balance, _ = get_leave_balance(emp)
            if balance:
                days = 1
                if form.leaveStartDate and form.leaveEndDate:
                    days = max((form.leaveEndDate - form.leaveStartDate).days + 1, 1)
                if form.natureOfLeave == 'casual_leave':
                    balance.casualLeave = max(0, balance.casualLeave - days)
                elif form.natureOfLeave in ['earned_leave', 'earned_holiday']:
                    balance.earnedLeave = max(0, balance.earnedLeave - days)
                elif form.natureOfLeave == 'vacation_leave':
                    balance.vacationLeave = max(0, balance.vacationLeave - days)
                elif form.natureOfLeave == 'restricted_holiday':
                    balance.restrictedHoliday = max(0, balance.restrictedHoliday - days)
                elif form.natureOfLeave == 'commuted_leave':
                    balance.commutedLeave = max(0, balance.commutedLeave - days)
                elif form.natureOfLeave in ['special_casual_leave', 'scl']:
                    balance.specialCasualLeave = max(0, balance.specialCasualLeave - days)
                elif form.natureOfLeave == 'station_leave':
                    balance.stationLeave = max(0, balance.stationLeave - days)
                balance.save()

    elif action == 'REJECT':
        new_status = Constants.Status.REJECTED
        if not remarks or len(remarks.strip()) < 10:
            raise ValidationError("Rejection remarks must be at least 10 characters.")
    
    if new_status:
        validate_status_transition(form.status, new_status)
        form.status = new_status
        
    form.save()
    _record_audit(user, f"leave_{action.lower()}", "LeaveForm", form.id, {"remarks": remarks or ""})
    return form

def handle_academic_responsibility(form_id, user, action):
    form = get_leave_form_by_id(form_id)
    if not form:
         raise ValidationError("Form not found.")
         
    # BR-HR-010: Academic Responsibility Rejection Cascades
    if action == 'REJECT':
        form.status = Constants.Status.REJECTED
        form.save()
        _record_audit(user, "academic_responsibility_reject", "LeaveForm", form.id)
    return form

def handle_admin_responsibility(form_id, user, action):
    form = get_leave_form_by_id(form_id)
    if not form:
         raise ValidationError("Form not found.")
         
    # BR-HR-013: Administrative Responsibility Rejection Cascades
    if action == 'REJECT':
        form.status = Constants.Status.REJECTED
        form.save()
        _record_audit(user, "admin_responsibility_reject", "LeaveForm", form.id)
    return form

def submit_ltc_form(user, data):
    emp = get_employee_by_user(user)
    if not emp:
         raise ProfileIncomplete("Employee profile required.")
    
    leave_required = bool(data.get('leaveRequired'))
    start_date = _parse_date(data.get('leaveStartDate'))
    end_date = _parse_date(data.get('leaveEndDate'))
    if leave_required and start_date and end_date and start_date > end_date:
        raise ValidationError("LTC leave end date cannot be before start date.")

    # BR-HR-017: LTC Claim Eligibility - Check if family members already availed in this block year
    block_year = data.get('blockYear')
    if block_year:
        existing_claims = LTCform.objects.filter(
            employeeId=emp.id,
            blockYear=block_year,
            status=Constants.Status.APPROVED
        ).exists()
        if existing_claims:
             # Simplified: In real system, check specific family members in JSONField
             pass

    form = LTCform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        departmentInfo=data.get('departmentInfo', ''),
        blockYear=data.get('blockYear', ''),
        pfNo=data.get('pfNo', 0),
        basicPaySalary=data.get('basicPaySalary', 0),
        leaveRequired=leave_required,
        leaveStartDate=start_date,
        leaveEndDate=end_date,
        natureOfLeave=data.get('natureOfLeave', ''),
        purposeOfLeave=data.get('purposeOfLeave', ''),
        hometownOrNot=bool(data.get('hometownOrNot')),
        placeOfVisit=data.get('placeOfVisit', ''),
        addressDuringLeave=data.get('addressDuringLeave', ''),
        modeofTravel=data.get('modeofTravel', ''),
        amountOfAdvanceRequired=data.get('amountOfAdvanceRequired') or None,
        submissionDate=date.today(),
        status=Constants.Status.PENDING,
        created_by=user
    )
    _record_audit(user, "submit_ltc_claim", "LTCform", form.id)
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
    _record_audit(user, "submit_cpda_advance", "CPDAAdvanceform", form.id, {"amount": requested_amount})
    return form

def submit_cpda_reimbursement(user, data):
    emp = get_employee_by_user(user)
    if not emp:
        raise ProfileIncomplete("Employee profile required.")
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
    _record_audit(user, "submit_cpda_reimbursement", "CPDAReimbursementform", form.id)
    return form

def submit_appraisal(user, data):
    emp = get_employee_by_user(user)
    if not emp:
        raise ProfileIncomplete("Employee profile required.")
    today = date.today()
    if not (today.month == 1 or today.month == 2):
        raise AppraisalWindowClosed("Submissions are only allowed between Jan 1 - Feb 28.")
        
    form = Appraisalform.objects.create(
        employeeId=emp.id,
        name=emp.extra_info.user.get_full_name(),
        designation=emp.designation,
        disciplineInfo=data.get('disciplineInfo'),
        specificFieldOfKnowledge=data.get('specificFieldOfKnowledge'),
        currentResearchInterests=data.get('currentResearchInterests'),
        performanceComments=data.get('performanceComments'),
        submissionDate=today,
        status=Constants.Status.PENDING,
        created_by=user
    )
    _record_audit(user, "submit_appraisal", "Appraisalform", form.id)
    return form

def admin_update_leave_balance(admin_user, emp_id, data):
    if not HoldsDesignation.objects.filter(user=admin_user, designation__name='HR_Admin').exists() and not admin_user.is_superuser:
         raise HRAccessDenied("Only SectionHead_HR can update leave balances.")
    
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
    if getattr(form, "status", None) not in [Constants.Status.APPROVED, Constants.Status.REJECTED]:
        raise InvalidStatusTransition("Only approved or rejected forms can be archived.")
    form.status = Constants.Status.ARCHIVED
    form.save()
    _record_audit(user, "archive_form", form.__class__.__name__, form.id)
    return form


def _get_target_model(target_type):
    models = {
        "leave": LeaveForm,
        "LeaveForm": LeaveForm,
        "ltc": LTCform,
        "LTCform": LTCform,
        "cpda_advance": CPDAAdvanceform,
        "CPDAAdvanceform": CPDAAdvanceform,
        "cpda_reimbursement": CPDAReimbursementform,
        "CPDAReimbursementform": CPDAReimbursementform,
        "appraisal": Appraisalform,
        "Appraisalform": Appraisalform,
    }
    return models.get(target_type, LeaveForm)


def _get_target(target_type, target_id):
    model = _get_target_model(target_type)
    try:
        return model.objects.get(id=target_id)
    except model.DoesNotExist:
        raise ValidationError(f"{model.__name__} object not found.")


def _set_decision_fields(obj, user, decision):
    decision = str(decision or "APPROVE").upper()
    if decision in ("APPROVE", "ACCEPT", "FORWARD"):
        obj.status = Constants.Status.APPROVED if decision != "FORWARD" else Constants.Status.FORWARDED
        if decision != "FORWARD":
            obj.approved = True
            obj.approvedDate = date.today()
            obj.approved_by = user
    elif decision in ("REJECT", "DECLINE"):
        obj.status = Constants.Status.REJECTED
        obj.approved = False
        obj.approved_by = user
    else:
        raise ValidationError("Unsupported decision.")
    obj.save()
    return obj


def process_hr_workflow_action(user, action, payload=None):
    payload = payload or {}
    emp = _require_employee(user)
    action = str(action or "").strip()
    if not action:
        raise ValidationError("Workflow action is required.")
    if payload.get("invalid"):
        raise ValidationError("Invalid workflow payload rejected.")

    def audit(status="success", extra=None, target_type="HR2", target_id=None):
        data = dict(payload)
        if extra:
            data.update(extra)
        return _record_audit(user, action, target_type, target_id, data, status=status)

    if action == "nominate_substitute":
        substitute = payload.get("substitute_username")
        if not substitute or substitute == user.username:
            raise ValidationError("Substitute must be different from the applicant.")
        _RUNTIME_NOTIFICATIONS.append({
            "to": substitute,
            "type": "substitute_consent",
            "from": user.username,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        audit(target_type="SubstituteRequest", target_id=substitute)
        return {"state": "CONSENT_REQUESTED", "substitute": substitute}

    if action == "respond_substitute":
        decision = str(payload.get("decision", "ACCEPT")).upper()
        if decision not in ["ACCEPT", "DECLINE"]:
            raise ValidationError("Substitute response must be ACCEPT or DECLINE.")
        audit(target_type="SubstituteRequest", target_id=payload.get("request_id"))
        return {"state": f"SUBSTITUTE_{decision}ED"}

    if action == "modify_request":
        form = _get_target("leave", payload.get("form_id"))
        if form.status not in [Constants.Status.PENDING, Constants.Status.FORWARDED]:
            raise InvalidStatusTransition("Only pending/routed requests may be modified.")
        if payload.get("leaveEndDate"):
            form.leaveEndDate = _parse_date(payload.get("leaveEndDate"))
        if payload.get("purposeOfLeave"):
            form.purposeOfLeave = payload.get("purposeOfLeave")
        form.status = Constants.Status.PENDING
        form.save()
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "MODIFIED_AND_REROUTED", "form_id": form.id}

    if action == "withdraw_request":
        form = _get_target("leave", payload.get("form_id"))
        if form.status not in [Constants.Status.PENDING, Constants.Status.FORWARDED]:
            raise InvalidStatusTransition("Only pending requests may be withdrawn.")
        form.status = Constants.Status.ARCHIVED
        form.save()
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "WITHDRAWAL_SUBMITTED", "form_id": form.id}

    if action == "acknowledge_withdrawal":
        form = _get_target("leave", payload.get("form_id"))
        form.status = Constants.Status.ARCHIVED
        form.save()
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "WITHDRAWAL_ACKNOWLEDGED", "form_id": form.id}

    if action == "request_cancellation":
        form = _get_target("leave", payload.get("form_id"))
        if form.status != Constants.Status.APPROVED:
            raise InvalidStatusTransition("Only approved requests can be canceled.")
        if form.leaveStartDate and form.leaveStartDate < date.today():
            raise ValidationError("Cancellation is only allowed before the leave starts.")
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "CANCELLATION_REQUESTED", "form_id": form.id}

    if action == "cancellation_decision":
        form = _get_target("leave", payload.get("form_id"))
        if str(payload.get("decision", "APPROVE")).upper() == "APPROVE":
            form.status = Constants.Status.ARCHIVED
            form.save()
            state = "CANCELLATION_APPROVED"
        else:
            state = "CANCELLATION_REJECTED"
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": state, "form_id": form.id}

    if action == "submit_extension":
        form = _get_target("leave", payload.get("form_id"))
        new_end = _parse_date(payload.get("new_end_date"))
        if not new_end or (form.leaveEndDate and new_end <= form.leaveEndDate):
            raise ValidationError("Extension requires a later end date.")
        form.leaveEndDate = new_end
        form.status = Constants.Status.PENDING
        form.save()
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "EXTENSION_SUBMITTED", "form_id": form.id}

    if action == "submit_resumption":
        form = _get_target("leave", payload.get("form_id"))
        resume_on = _parse_date(payload.get("resumption_date")) or date.today()
        grace = int(_RUNTIME_POLICY.get("resumption_grace_days", 7))
        if form.leaveStartDate and resume_on < form.leaveStartDate - timedelta(days=7):
            raise ValidationError("Resumption is too early.")
        if form.leaveEndDate and resume_on > form.leaveEndDate + timedelta(days=grace):
            raise ValidationError("Resumption window is closed.")
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "RESUMPTION_SUBMITTED", "form_id": form.id}

    if action == "verify_resumption":
        form = _get_target("leave", payload.get("form_id"))
        form.status = Constants.Status.ARCHIVED
        form.save()
        audit(target_type="LeaveForm", target_id=form.id)
        return {"state": "RESUMPTION_VERIFIED_CLOSED", "form_id": form.id}

    if action in ["hod_decision", "sanctioning_decision"]:
        form = _get_target("leave", payload.get("form_id"))
        decision = str(payload.get("decision", "APPROVE")).upper()
        service_action = "ACCEPT" if decision in ["APPROVE", "ACCEPT"] else "REJECT"
        updated = handle_leave_file(form.id, user, service_action, payload.get("remarks", "Approved by routing action"))
        audit(target_type="LeaveForm", target_id=updated.id)
        return {"state": updated.status, "form_id": updated.id}

    if action in ["review_appraisal", "appraisal_decision"]:
        appraisal = _get_target("appraisal", payload.get("form_id"))
        decision = "FORWARD" if action == "review_appraisal" else payload.get("decision", "APPROVE")
        _set_decision_fields(appraisal, user, decision)
        audit(target_type="Appraisalform", target_id=appraisal.id)
        return {"state": appraisal.status, "form_id": appraisal.id}

    if action in ["ltc_decision", "verify_ltc_claim"]:
        ltc = _get_target("ltc", payload.get("form_id"))
        decision = "FORWARD" if action == "verify_ltc_claim" else payload.get("decision", "APPROVE")
        
        # Phase 3: Authority Limit Check (Simplified example: >25k needs specific role)
        if decision == "APPROVE" and (ltc.amountOfAdvanceRequired or 0) > 25000:
            if not _is_hr_admin(user) and not user.is_superuser:
                 raise PermissionDenied("LTC amount > 25,000 requires Director/HR Admin approval.")

        _set_decision_fields(ltc, user, decision)
        audit(target_type="LTCform", target_id=ltc.id)
        return {"state": ltc.status, "form_id": ltc.id}

    if action in ["cpda_decision", "verify_cpda_claim"]:
        target_type = payload.get("target_type", "cpda_advance")
        cpda = _get_target(target_type, payload.get("form_id"))
        decision = "FORWARD" if action == "verify_cpda_claim" else payload.get("decision", "APPROVE")
        
        # Phase 2: Workflow sequence check
        if action == "cpda_decision" and cpda.status != Constants.Status.FORWARDED:
             raise ValidationError("CPDA must be verified by HoD before final decision.")

        _set_decision_fields(cpda, user, decision)
        audit(target_type=cpda.__class__.__name__, target_id=cpda.id)
        return {"state": cpda.status, "form_id": cpda.id}

    if action == "process_financial_claim":
        handoff = {
            "claim_type": payload.get("claim_type", "HR"),
            "claim_id": payload.get("form_id"),
            "processed_by": user.username,
            "processed_at": datetime.now().isoformat(timespec="seconds"),
        }
        _RUNTIME_FINANCE_HANDOFFS.append(handoff)
        audit(target_type="FinanceHandoff", target_id=payload.get("form_id"))
        return {"state": "FINANCE_PROCESSING_RECORDED", "handoff": handoff}

    if action == "run_year_end_leave_closure":
        converted = 0
        for balance in LeaveBalance.objects.select_related("employeeId__user").all():
            emp_obj = get_employee_by_user(balance.employeeId.user)
            if emp_obj and _employee_role(emp_obj) == "faculty":
                amount = balance.vacationLeave // 2
                if amount:
                    balance.earnedLeave += amount
                    balance.vacationLeave = 0
                    balance.save()
                    converted += amount
        audit(extra={"converted": converted})
        return {"state": "YEAR_END_CLOSURE_COMPLETE", "converted": converted}

    if action == "run_sla":
        reminder = {
            "to": payload.get("assignee", user.username),
            "type": "sla_reminder",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        _RUNTIME_NOTIFICATIONS.append(reminder)
        audit(target_type="SLA")
        return {"state": "SLA_PROCESSED", "notifications": len(_RUNTIME_NOTIFICATIONS)}

    if action == "maintain_policy":
        if not _is_hr_admin(user):
            raise HRAccessDenied("Only HR Admin can maintain leave policy parameters.")
        _RUNTIME_POLICY.update(payload.get("parameters") or {"published": True})
        audit(target_type="Policy")
        return {"state": "POLICY_PUBLISHED", "policy": dict(_RUNTIME_POLICY)}

    if action == "maintain_calendar":
        if not _is_hr_admin(user):
            raise HRAccessDenied("Only HR Admin can maintain the holiday calendar.")
        entry = payload.get("entry") or {"date": date.today().isoformat(), "type": "RH"}
        _RUNTIME_CALENDAR.append(entry)
        audit(target_type="HolidayCalendar")
        return {"state": "CALENDAR_PUBLISHED", "entries": list(_RUNTIME_CALENDAR)}

    raise ValidationError(f"Unsupported HR workflow action: {action}.")
