from django.contrib import admin
from .models import (
    Employee, EmpConfidentialDetails, EmpDependents,
    LeaveForm, LeaveBalance, LeavePerYear, LeaveClaim,
    LTCform, CPDAAdvanceform, CPDAReimbursementform, Appraisalform
)

admin.site.register(Employee)
admin.site.register(EmpConfidentialDetails)
admin.site.register(EmpDependents)
admin.site.register(LeaveForm)
admin.site.register(LeaveBalance)
admin.site.register(LeavePerYear)
admin.site.register(LeaveClaim)
admin.site.register(LTCform)
admin.site.register(CPDAAdvanceform)
admin.site.register(CPDAReimbursementform)
admin.site.register(Appraisalform)