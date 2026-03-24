from django.db import models
from applications.globals.models import ExtraInfo
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User

class Constants:
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class Department(models.TextChoices):
        CSE = 'CSE', 'CSE'
        ME = 'ME', 'Mechanical'
        ECE = 'ECE', 'ECE'
        DESIGN = 'DESIGN', 'DESIGN'

    class Category(models.TextChoices):
        SC = 'SC', 'SC'
        ST = 'ST', 'ST'
        OBC = 'OBC', 'OBC'
        GENERAL = 'GENERAL', 'GENERAL'
        PWD = 'PWD', 'PWD'

    class MartialStatus(models.TextChoices):
        MARRIED = 'MARRIED', 'MARRIED'
        UNMARRIED = 'UN-MARRIED', 'UN-MARRIED'
        WIDOW = 'WIDOW', 'WIDOW'

    class BloodGroup(models.TextChoices):
        AB_POS = 'AB+', 'AB+'
        O_POS = 'O+', 'O+'
        AB_NEG = 'AB-', 'AB-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        O_NEG = 'O-', 'O-'
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'

    class ForeignService(models.TextChoices):
        LIEN = 'LIEN', 'LIEN'
        DEPUTATION = 'DEPUTATION', 'DEPUTATION'
        OTHER = 'OTHER', 'OTHER'

    class EmployeeType(models.TextChoices):
        FACULTY = 'FACULTY', 'Faculty'
        STAFF = 'STAFF', 'Staff'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        FORWARDED = 'FORWARDED', 'Forwarded'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class ApplicationType(models.TextChoices):
        LEAVE = 'LEAVE', 'Leave'
        LTC = 'LTC', 'LTC'
        CPDA_ADVANCE = 'CPDA_ADVANCE', 'CPDA Advance'
        CPDA_REIMBURSEMENT = 'CPDA_REIMBURSEMENT', 'CPDA Reimbursement'
        APPRAISAL = 'APPRAISAL', 'Appraisal'

# Employee model
class Employee(models.Model):
    extra_info = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
    employee_type = models.CharField(max_length=20, choices=Constants.EmployeeType.choices, default=Constants.EmployeeType.FACULTY)
    father_name = models.CharField(max_length=40, default='')
    mother_name = models.CharField(max_length=40, default='')
    religion = models.CharField(max_length=40, default='')
    category = models.CharField(max_length=50, null=False, choices=Constants.Category.choices)
    cast = models.CharField(max_length=40, default='')
    home_state = models.CharField(max_length=40, default='')
    home_district = models.CharField(max_length=40, default='')
    date_of_joining = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=40, default='')
    blood_group = models.CharField(max_length=50, choices=Constants.BloodGroup.choices)

    def __str__(self):
        return self.extra_info.user.first_name if self.extra_info and self.extra_info.user else str(self.id)

# table for employee  confidential details
class EmpConfidentialDetails(models.Model):
    extra_info = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
    aadhar_no = models.BigIntegerField(default=0, validators=[MaxValueValidator(999999999999), MinValueValidator(99999999999)])
    maritial_status = models.CharField(max_length=50, null=False, choices=Constants.MartialStatus.choices)
    bank_account_no = models.BigIntegerField(default=0) # Changed from Integer to BigInteger
    salary = models.IntegerField(default=0)

    def __str__(self):
        return self.extra_info.user.first_name if self.extra_info and self.extra_info.user else str(self.id)

# table for employee's dependent details
class EmpDependents(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE) # Changed to ForeignKey as one employee can have multiple dependents
    name = models.CharField(max_length=100, default='')
    gender = models.CharField(max_length=50, choices=Constants.Gender.choices)
    dob = models.DateField(max_length=6, null=True)
    relationship = models.CharField(max_length=40, default='')

    def __str__(self):
        return self.name

class ForeignService(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    start_date = models.DateField(max_length=6, null=True, blank=True)
    end_date = models.DateField(max_length=6, null=True, blank=True)
    job_title = models.CharField(max_length=50, default='')
    organisation = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=300, default='')
    salary_source = models.CharField(max_length=100, default='')
    designation = models.CharField(max_length=100, default='')
    service_type = models.CharField(max_length=100, choices=Constants.ForeignService.choices)

    def __str__(self):
        return self.extra_info.user.first_name if self.extra_info and self.extra_info.user else str(self.id)

class EmpAppraisalForm(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    year = models.DateField(max_length=6, null=True, blank=True)
    appraisal_form = models.FileField(upload_to='Hr2/appraisal_form', null=True, default=" ")

    def __str__(self):
        return self.extra_info.user.first_name if self.extra_info and self.extra_info.user else str(self.id)

class WorkAssignemnt(models.Model):
    extra_info = models.ForeignKey(ExtraInfo, on_delete=models.CASCADE)
    start_date = models.DateField(max_length=6, null=True, blank=True)
    end_date = models.DateField(max_length=6, null=True, blank=True)
    job_title = models.CharField(max_length=50, default='')
    orders_copy = models.FileField(blank=True, null=True)

class LeavePerYear(models.Model):
    id = models.AutoField(primary_key=True)
    casual_leave = models.IntegerField(default=8)
    restricted_holiday = models.IntegerField(default=2)
    earned_leave = models.IntegerField(default=15)
    vacation_leave = models.IntegerField(default=60)
    commuted_leave = models.IntegerField(default=20)
    special_casual_leave = models.IntegerField(default=15)
    year = models.IntegerField(default=2026) 

class LeaveBalance(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.OneToOneField(ExtraInfo, on_delete=models.CASCADE)
    casualLeave = models.IntegerField(default=0)
    specialCasualLeave = models.IntegerField(default=0)
    earnedLeave = models.IntegerField(default=0)
    commutedLeave = models.IntegerField(default=0)
    restrictedHoliday = models.IntegerField(default=0)
    stationLeave = models.IntegerField(default=0)
    vacationLeave = models.IntegerField(default=0)

class LeaveForm(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=40,null=True)
    designation = models.CharField(max_length=40,null=True)
    submissionDate = models.DateField(blank=True, null=True)
    pfNo = models.IntegerField(null=True)
    departmentInfo = models.CharField(max_length=40,null=True)
    natureOfLeave = models.TextField(max_length=40,null=True)
    leaveStartDate = models.DateField(blank=True, null=True)
    leaveEndDate = models.DateField(blank=True, null=True)
   
    purposeOfLeave = models.TextField(max_length=40,null=True)
    addressDuringLeave = models.TextField(max_length=40, blank=True, null=True)

    academicResponsibility = models.TextField(max_length=40, blank=True, null=True)
    addministrativeResponsibiltyAssigned = models.TextField(max_length=40,null=True)

    status = models.CharField(max_length=20, choices=Constants.Status.choices, default=Constants.Status.PENDING)
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Leave_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Leave_approved_by')
    pdf_file = models.FileField(upload_to='Hr2/leave_forms/', null=True, blank=True)

class LeaveClaim(models.Model):
    id = models.AutoField(primary_key=True)
    leaveForm = models.OneToOneField(LeaveForm, on_delete=models.CASCADE)
    days_taken = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

class LTCform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField()
    name = models.CharField(max_length=100, null=True)
    blockYear = models.TextField() 
    pfNo = models.IntegerField()
    basicPaySalary = models.IntegerField(null=True)
    designation = models.CharField(max_length=50)
    departmentInfo = models.CharField(max_length=50)
    leaveRequired = models.BooleanField(default=False,null=True) 
    leaveStartDate = models.DateField(null=True, blank=True)
    leaveEndDate = models.DateField(null=True, blank=True)
    dateOfDepartureForFamily = models.DateField(null=True, blank=True) 
    natureOfLeave = models.TextField(null=True,blank=True)
    purposeOfLeave = models.TextField(null=True,blank=True)
    hometownOrNot = models.BooleanField(default=False)
    placeOfVisit = models.TextField(max_length=100, null=True, blank=True) 
    addressDuringLeave = models.TextField(null=True)
    modeofTravel = models.TextField(max_length=10, null=True,blank=True) 
    detailsOfFamilyMembersAlreadyDone = models.JSONField(null=True,blank=True)
    detailsOfFamilyMembersAboutToAvail = models.JSONField(max_length=100, null=True,blank=True) 
    detailsOfDependents = models.JSONField(blank=True,null=True) 
    amountOfAdvanceRequired = models.IntegerField(null=True, blank=True)
    certifiedThatFamilyDependents = models.BooleanField(blank=True,null=True) 
    certifiedThatAdvanceTakenOn = models.DateField(null=True, blank=True) 
    adjustedMonth = models.TextField(max_length=50, null=True,blank=True)
    submissionDate = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=Constants.Status.choices, default=Constants.Status.PENDING)
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='LTC_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='LTC_approved_by')

class CPDAAdvanceform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=40,null=True)
    designation = models.CharField(max_length=40,null=True)
    pfNo = models.IntegerField(null=True)
    purpose = models.TextField(max_length=40, null=True)
    amountRequired = models.IntegerField(null=True)
    advanceDueAdjustment = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
   
    submissionDate = models.DateField(blank=True, null=True)
   
    balanceAvailable = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advanceAmountPDA = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amountCheckedInPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
   
    status = models.CharField(max_length=20, choices=Constants.Status.choices, default=Constants.Status.PENDING)
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDA_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDA_approved_by')

class CPDAReimbursementform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    pfNo = models.IntegerField()
    advanceTaken = models.IntegerField()
    purpose = models.TextField()
    adjustmentSubmitted = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    balanceAvailable = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    advanceDueAdjustment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    advanceAmountPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amountCheckedInPDA = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    submissionDate = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Constants.Status.choices, default=Constants.Status.PENDING)
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDAR_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='CPDAR_approved_by')

class Appraisalform(models.Model):
    id = models.AutoField(primary_key=True)
    employeeId = models.IntegerField(null=True)
    name = models.CharField(max_length=22)
    designation = models.CharField(max_length=50)
    disciplineInfo = models.CharField(max_length=22, null=True)
    specificFieldOfKnowledge = models.TextField(max_length=40, null=True)
    currentResearchInterests = models.TextField(max_length=40, null=True)
    coursesTaught = models.JSONField(max_length=100, null=True)
    newCoursesIntroduced = models.JSONField(max_length=100, null=True)
    newCoursesDeveloped = models.JSONField(max_length=100, null=True)
    otherInstructionalTasks = models.TextField(max_length=100, null=True)
    thesisSupervision = models.JSONField(max_length=100, null=True)
    sponsoredReseachProjects = models.JSONField(max_length=100, null=True)
    otherResearchElement = models.TextField(max_length=40, null=True)
    publication = models.TextField(max_length=40, null=True)
    referredConference = models.TextField(max_length=40, null=True)
    conferenceOrganised = models.TextField(max_length=40, null=True)
    membership = models.TextField(max_length=40, null=True)
    honours = models.TextField(max_length=40, null=True)
    editorOfPublications = models.TextField(max_length=40, null=True)
    expertLectureDelivered = models.TextField(max_length=40, null=True)
    membershipOfBOS = models.TextField(max_length=40, null=True)
    otherExtensionTasks = models.TextField(max_length=40, null=True)
    administrativeAssignment = models.TextField(max_length=40, null=True)
    serviceToInstitute = models.TextField(max_length=40, null=True)
    otherContribution = models.TextField(max_length=40, null=True)
    performanceComments = models.TextField(max_length=100, null=True)
    submissionDate = models.DateField(max_length=6, null=True)
    status = models.CharField(max_length=20, choices=Constants.Status.choices, default=Constants.Status.PENDING)
    approved = models.BooleanField(null=True)
    approvedDate = models.DateField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Appraisal_created_by')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='Appraisal_approved_by')
