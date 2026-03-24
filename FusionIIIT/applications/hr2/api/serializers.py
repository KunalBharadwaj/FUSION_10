from rest_framework import serializers
from applications.hr2.models import (
    Employee, EmpConfidentialDetails, EmpDependents,
    LeaveBalance, LeavePerYear, LeaveForm, LeaveClaim,
    LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform
)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_type', 'father_name', 'mother_name', 'religion', 'category', 'cast', 'home_state', 'home_district', 'date_of_joining', 'designation', 'blood_group']

class EmpConfidentialDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpConfidentialDetails
        fields = ['aadhar_no', 'maritial_status', 'bank_account_no', 'salary']

class EmpDependentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpDependents
        fields = ['name', 'gender', 'dob', 'relationship']

class LeaveFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveForm
        fields = ['id', 'employeeId', 'name', 'designation', 'submissionDate', 'pfNo', 'departmentInfo', 'natureOfLeave', 'leaveStartDate', 'leaveEndDate', 'purposeOfLeave', 'addressDuringLeave', 'academicResponsibility', 'addministrativeResponsibiltyAssigned', 'status', 'approved', 'approvedDate']
        read_only_fields = ['status', 'approved', 'approvedDate', 'submissionDate']

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['casualLeave', 'specialCasualLeave', 'earnedLeave', 'commutedLeave', 'restrictedHoliday', 'stationLeave', 'vacationLeave']

class LeavePerYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePerYear
        fields = ['casual_leave', 'restricted_holiday', 'earned_leave', 'vacation_leave', 'commuted_leave', 'special_casual_leave', 'year']

class LeaveClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveClaim
        fields = ['days_taken', 'start_date', 'end_date']

class LTCSerializer(serializers.ModelSerializer):
    class Meta:
        model = LTCform
        fields = ['id', 'employeeId', 'name', 'blockYear', 'pfNo', 'basicPaySalary', 'designation', 'departmentInfo', 'leaveRequired', 'leaveStartDate', 'leaveEndDate', 'dateOfDepartureForFamily', 'natureOfLeave', 'purposeOfLeave', 'hometownOrNot', 'placeOfVisit', 'addressDuringLeave', 'modeofTravel', 'amountOfAdvanceRequired', 'submissionDate', 'status']
        read_only_fields = ['status', 'submissionDate']

class CPDAAdvanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDAAdvanceform
        fields = ['id', 'employeeId', 'name', 'designation', 'pfNo', 'purpose', 'amountRequired', 'submissionDate', 'status']
        read_only_fields = ['status', 'submissionDate']

class CPDAReimbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPDAReimbursementform
        fields = ['id', 'employeeId', 'name', 'designation', 'pfNo', 'advanceTaken', 'purpose', 'submissionDate', 'status']
        read_only_fields = ['status', 'submissionDate']

class AppraisalformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appraisalform
        fields = ['id', 'employeeId', 'name', 'designation', 'disciplineInfo', 'specificFieldOfKnowledge', 'currentResearchInterests', 'performanceComments', 'submissionDate', 'status']
        read_only_fields = ['status', 'submissionDate']

class FormInitialsSerializer(serializers.Serializer):
    name = serializers.CharField()
    designation = serializers.CharField()
    department = serializers.CharField()
    pfNo = serializers.IntegerField(required=False)

class LeaveInboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveForm
        fields = ['id', 'name', 'designation', 'natureOfLeave', 'leaveStartDate', 'leaveEndDate', 'status']

class LeaveSearchResultSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='extra_info.user.first_name', read_only=True)
    last_name = serializers.CharField(source='extra_info.user.last_name', read_only=True)
    username = serializers.CharField(source='extra_info.user.username', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name', 'username', 'designation']
