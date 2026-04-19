from django.urls import path
from .views import (
    get_leave_balance, submit_leave_form, get_leave_requests, get_leave_inbox, handle_leave_file,
    search_employees, LTC, CPDAAdvance, CPDAReimbursement, Appraisal, workflow_action
)

urlpatterns = [
    path('get_leave_balance/', get_leave_balance, name='get_leave_balance'),
    path('leave-balance/', get_leave_balance, name='leave_balance_alias'),
    path('submit_leave_form/', submit_leave_form, name='submit_leave_form'),
    path('submit-leave/', submit_leave_form, name='submit_leave_alias'),
    path('get_leave_requests/', get_leave_requests, name='get_leave_requests'),
    path('leave-requests/', get_leave_requests, name='leave_requests_alias'),
    path('get_leave_inbox/', get_leave_inbox, name='get_leave_inbox'),
    path('leave-inbox/', get_leave_inbox, name='leave_inbox_alias'),
    path('handle_leave_file/<int:id>/', handle_leave_file, name='handle_leave_file'),
    path('search_employees/', search_employees, name='search_employees'),
    path('search-employees/', search_employees, name='search_employees_alias'),
    path('ltc/', LTC.as_view(), name='ltc'),
    path('cpdaadv/', CPDAAdvance.as_view(), name='cpdaadv'),
    path('cpda-advance/', CPDAAdvance.as_view(), name='cpda_advance_alias'),
    path('cpdareim/', CPDAReimbursement.as_view(), name='cpdareim'),
    path('cpda-reimbursement/', CPDAReimbursement.as_view(), name='cpda_reimbursement_alias'),
    path('appraisal/', Appraisal.as_view(), name='appraisal'),
    path('workflow_action/', workflow_action, name='workflow_action'),
]
