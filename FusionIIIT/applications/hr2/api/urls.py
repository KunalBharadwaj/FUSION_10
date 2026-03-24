from django.urls import path
from .views import (
    get_leave_balance, submit_leave_form, get_leave_requests, get_leave_inbox, handle_leave_file,
    search_employees, LTC, CPDAAdvance, CPDAReimbursement, Appraisal
)

urlpatterns = [
    path('get_leave_balance/', get_leave_balance, name='get_leave_balance'),
    path('submit_leave_form/', submit_leave_form, name='submit_leave_form'),
    path('get_leave_requests/', get_leave_requests, name='get_leave_requests'),
    path('get_leave_inbox/', get_leave_inbox, name='get_leave_inbox'),
    path('handle_leave_file/<int:id>/', handle_leave_file, name='handle_leave_file'),
    path('search_employees/', search_employees, name='search_employees'),
    path('ltc/', LTC.as_view(), name='ltc'),
    path('cpdaadv/', CPDAAdvance.as_view(), name='cpdaadv'),
    path('cpdareim/', CPDAReimbursement.as_view(), name='cpdareim'),
    path('appraisal/', Appraisal.as_view(), name='appraisal'),
]
