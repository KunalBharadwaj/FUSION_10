from django.conf.urls import url, include 
from django.contrib.auth.decorators import login_required

from applications.hr2 import views

app_name = 'hr2'

urlpatterns = [

    url(r'^$', login_required(views.service_book, login_url='/accounts/login'), name='hr2'),
    url(r'^hradmin/$', login_required(views.hr_admin, login_url='/accounts/login'), name='hradmin'),
    url(r'^edit/(?P<id>\d+)/$', login_required(views.edit_employee_details, login_url='/accounts/login'),
        name='editEmployeeDetails'),
    url(r'^viewdetails/(?P<id>\d+)/$',
        login_required(views.view_employee_details, login_url='/accounts/login'), name='viewEmployeeDetails'),
    url(r'^editServiceBook/(?P<id>\d+)/$',
        login_required(views.edit_employee_servicebook, login_url='/accounts/login'), name='editServiceBook'),
    url(r'^administrativeProfile/$', login_required(views.administrative_profile, login_url='/accounts/login'),
        name='administrativeProfile'),
    url(r'^addnew/$', login_required(views.add_new_user, login_url='/accounts/login'), name='addnew'),
    url(r'^ltc_form/(?P<id>\d+)/$', login_required(views.ltc_form, login_url='/accounts/login'),
        name='ltcForm'),
    
    url(r'^view_ltc_form/(?P<id>\d+)/$', login_required(views.view_ltc_form, login_url='/accounts/login'),
        name='view_ltc_form'),
    url(r'^form_mangement_ltc/',login_required(views.form_mangement_ltc, login_url='/accounts/login'), name='form_mangement_ltc'),
    url(r'dashboard/', login_required(views.dashboard, login_url='/accounts/login'), name='dashboard'),
    url(r'^form_mangement_ltc_hr/(?P<id>\d+)/$',login_required(views.form_mangement_ltc_hr, login_url='/accounts/login'), name='form_mangement_ltc_hr'),
    url(r'^form_mangement_ltc_hod/',login_required(views.form_mangement_ltc_hod, login_url='/accounts/login'), name='form_mangement_ltc_hod'),
    url(r'^search_employee/', login_required(views.search_employee, login_url='/accounts/login'), name='search_employee'),
    url(r'^track_file/(?P<id>\d+)/$', login_required(views.track_file, login_url='/accounts/login'), name='track_file'),
    url('form_view_ltc/(?P<id>\d+)/$', login_required(views.form_view_ltc, login_url='/accounts/login'), name='form_view_ltc'),
    # url('file_handle/', views.file_handle, name='file_handle'),
    url('file_handle_cpda/', login_required(views.file_handle_cpda, login_url='/accounts/login'), name='file_handle_cpda'),
    url('file_handle_leave/', login_required(views.file_handle_leave, login_url='/accounts/login'), name='file_handle_leave'),
    url('file_handle_ltc/', login_required(views.file_handle_ltc, login_url='/accounts/login'), name='file_handle_ltc'),
    url('file_handle_appraisal/', login_required(views.file_handle_appraisal, login_url='/accounts/login'), name='file_handle_appraisal'),
    url('file_handle_cpda_reimbursement/', login_required(views.file_handle_cpda_reimbursement, login_url='/accounts/login'), name='file_handle_cpda_reimbursement'),

    url(r'^cpda_form/(?P<id>\d+)/$', login_required(views.cpda_form, login_url='/accounts/login'),name='cpdaForm'),
    url(r'^view_cpda_form/(?P<id>\d+)/$', login_required(views.view_cpda_form, login_url='/accounts/login'),name='view_cpda_form'),
    url(r'^form_mangement_cpda/',login_required(views.form_mangement_cpda, login_url='/accounts/login'), name='form_mangement_cpda'),
    url(r'^form_mangement_cpda_hr/(?P<id>\d+)/$',login_required(views.form_mangement_cpda_hr, login_url='/accounts/login'), name='form_mangement_cpda_hr'),
    url(r'^form_mangement_cpda_hod/',login_required(views.form_mangement_cpda_hod, login_url='/accounts/login'), name='form_mangement_cpda_hod'),
    url('form_view_cpda/(?P<id>\d+)/$', login_required(views.form_view_cpda, login_url='/accounts/login'), name='form_view_cpda'),
    url(r'^api/',include('applications.hr2.api.urls')),

    url(r'^cpda_reimbursement_form/(?P<id>\d+)/$', login_required(views.cpda_reimbursement_form, login_url='/accounts/login'),name='cpdaReimbursementForm'),
    url(r'^view_cpda_reimbursement_form/(?P<id>\d+)/$', login_required(views.view_cpda_reimbursement_form, login_url='/accounts/login'),name='view_cpda_reimbursement_form'),
    url(r'form_view_cpda_reimbursement/(?P<id>\d+)/$', login_required(views.form_view_cpda_reimbursement, login_url='/accounts/login'), name='form_view_cpda_reimbursement'),
    url(r'^form_mangement_cpda_reimbursement/',login_required(views.form_mangement_cpda_reimbursement, login_url='/accounts/login'), name='form_mangement_cpda_reimbursement'),
    url(r'^form_mangement_cpda_reimbursement_hr/(?P<id>\d+)/$',login_required(views.form_mangement_cpda_reimbursement_hr, login_url='/accounts/login'), name='form_mangement_cpda_reimbursement_hr'),
    url(r'^form_mangement_cpda_reimbursement_hod/',login_required(views.form_mangement_cpda_reimbursement_hod, login_url='/accounts/login'), name='form_mangement_cpda_reimbursement_hod'),

    url(r'^leave_form/(?P<id>\d+)/$', login_required(views.leave_form, login_url='/accounts/login'),name='leaveForm'),
    url(r'^view_leave_form/(?P<id>\d+)/$', login_required(views.view_leave_form, login_url='/accounts/login'),name='view_leave_form'),
    url(r'^form_mangement_leave/',login_required(views.form_mangement_leave, login_url='/accounts/login'), name='form_mangement_leave'),
    url(r'^form_mangement_leave_hr/(?P<id>\d+)/$',login_required(views.form_mangement_leave_hr, login_url='/accounts/login'), name='form_mangement_leave_hr'),
    url(r'^form_mangement_leave_hod/',login_required(views.form_mangement_leave_hod, login_url='/accounts/login'), name='form_mangement_leave_hod'),
    url('form_view_leave/(?P<id>\d+)/$', login_required(views.form_view_leave, login_url='/accounts/login'), name='form_view_leave'),



    url(r'^appraisal_form/(?P<id>\d+)/$', login_required(views.appraisal_form, login_url='/accounts/login'),name='appraisalForm'),
    url(r'^view_appraisal_form/(?P<id>\d+)/$', login_required(views.view_appraisal_form, login_url='/accounts/login'),name='view_appraisal_form'),
    url(r'^form_mangement_appraisal/',login_required(views.form_mangement_appraisal, login_url='/accounts/login'), name='form_mangement_appraisal'),
    url(r'^form_mangement_appraisal_hr/(?P<id>\d+)/$',login_required(views.form_mangement_appraisal_hr, login_url='/accounts/login'), name='form_mangement_appraisal_hr'),
   
    url(r'^form_view_appraisal/(?P<id>\d+)/$', login_required(views.form_view_appraisal, login_url='/accounts/login'), name='form_view_appraisal'),
    url(r'^getform/$', login_required(views.getform, login_url='/accounts/login') , name='getform'),
    url(r'^getformcpdaAdvance/$', login_required(views.getformcpdaAdvance, login_url='/accounts/login') , name='getformcpdaAdvance'),
    url(r'^getformLeave/$', login_required(views.getformLeave, login_url='/accounts/login') , name='getformLeave'),  
    url(r'^getformAppraisal/$', login_required(views.getformAppraisal, login_url='/accounts/login') , name='getformAppraisal'),
    url(r'^getformcpdaReimbursement/$', login_required(views.getformcpdaReimbursement, login_url='/accounts/login') , name='getformcpdaReimbursement'),

























]
