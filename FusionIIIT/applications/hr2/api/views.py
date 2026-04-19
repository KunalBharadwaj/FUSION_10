from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import PermissionDenied, ValidationError
import logging

from applications.hr2.services import (
    submit_leave_form as srv_submit_leave_form,
    handle_leave_file as srv_handle_leave_file,
    submit_ltc_form as srv_submit_ltc_form,
    submit_cpda_advance as srv_submit_cpda_advance,
    submit_cpda_reimbursement as srv_submit_cpda_reimbursement,
    submit_appraisal as srv_submit_appraisal,
    admin_update_leave_balance as srv_admin_update_leave_balance,
    process_hr_workflow_action as srv_process_hr_workflow_action,
    get_runtime_records as srv_get_runtime_records,
)
from applications.hr2.selectors import (
    get_employee_by_user, get_leave_balance as sel_get_leave_balance,
    get_leave_forms, get_leave_form_by_id as sel_get_leave_form_by_id,
    get_leave_inbox as sel_get_leave_inbox, search_employees as sel_search_employees,
    get_ltc_forms, get_cpda_advance_forms, get_cpda_reimbursement_forms, get_appraisal_forms
)
from applications.hr2.api.serializers import (
    LeaveBalanceSerializer, LeaveFormSerializer, LeaveInboxSerializer, LeaveSearchResultSerializer,
    LTCSerializer, CPDAAdvanceSerializer, CPDAReimbursementSerializer, AppraisalformSerializer
)


logger = logging.getLogger(__name__)


def _validation_error_message(error):
    if hasattr(error, 'message_dict'):
        return error.message_dict
    if hasattr(error, 'messages'):
        return error.messages
    return str(error)


def _unexpected_error_response(error, context_message):
    logger.exception(context_message)
    return Response(
        {"error": "An unexpected server error occurred. Please try again."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_balance(request):
    emp = get_employee_by_user(request.user)
    if not emp: return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    balance, _ = sel_get_leave_balance(emp)
    serializer = LeaveBalanceSerializer(balance)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_leave_form(request):
    try:
        form = srv_submit_leave_form(request.user, request.data)
        return Response(LeaveFormSerializer(form).data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return _unexpected_error_response(e, "submit_leave_form failed")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_requests(request):
    try:
        emp = get_employee_by_user(request.user)
        if not emp:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        forms = get_leave_forms(emp)
        return Response(LeaveFormSerializer(forms, many=True).data)
    except Exception as e:
        return _unexpected_error_response(e, "get_leave_requests failed")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leave_inbox(request):
    try:
        forms = sel_get_leave_inbox(request.user)
        return Response(LeaveInboxSerializer(forms, many=True).data)
    except Exception as e:
        return _unexpected_error_response(e, "get_leave_inbox failed")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_leave_file(request, id):
    try:
        action = request.data.get('action')
        remarks = request.data.get('remarks')
        forward_to = request.data.get('forward_to')
        forward_designation = request.data.get('forward_designation')
        form = srv_handle_leave_file(id, request.user, action, remarks, forward_to, forward_designation)
        return Response({"status": "success", "form_id": form.id})
    except ValidationError as e:
        return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return _unexpected_error_response(e, "handle_leave_file failed")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_employees(request):
    from django.contrib.auth.models import User
    from django.db.models import Q as DQ
    try:
        query = request.query_params.get('q', '')
        users = User.objects.filter(
            DQ(first_name__icontains=query) | DQ(username__icontains=query),
            is_active=True,
            extrainfo__user_type='faculty',
        ).exclude(id=request.user.id).distinct()
        data = [
            {
                "id": u.id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "username": u.username,
                "designation": "",
            }
            for u in users
        ]
        return Response(data)
    except Exception as e:
        return _unexpected_error_response(e, "search_employees failed")

class LTC(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            emp = get_employee_by_user(request.user)
            if not emp:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            forms = get_ltc_forms(emp)
            return Response(LTCSerializer(forms, many=True).data)
        except Exception as e:
            return _unexpected_error_response(e, "LTC GET failed")

    def post(self, request):
        try:
            form = srv_submit_ltc_form(request.user, request.data)
            return Response(LTCSerializer(form).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return _unexpected_error_response(e, "LTC POST failed")

class CPDAAdvance(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            emp = get_employee_by_user(request.user)
            if not emp:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            forms = get_cpda_advance_forms(emp)
            return Response(CPDAAdvanceSerializer(forms, many=True).data)
        except Exception as e:
            return _unexpected_error_response(e, "CPDAAdvance GET failed")

    def post(self, request):
        try:
            form = srv_submit_cpda_advance(request.user, request.data)
            return Response(CPDAAdvanceSerializer(form).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return _unexpected_error_response(e, "CPDAAdvance POST failed")

class CPDAReimbursement(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            emp = get_employee_by_user(request.user)
            if not emp:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            forms = get_cpda_reimbursement_forms(emp)
            return Response(CPDAReimbursementSerializer(forms, many=True).data)
        except Exception as e:
            return _unexpected_error_response(e, "CPDAReimbursement GET failed")

    def post(self, request):
        try:
            form = srv_submit_cpda_reimbursement(request.user, request.data)
            return Response(CPDAReimbursementSerializer(form).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return _unexpected_error_response(e, "CPDAReimbursement POST failed")

class Appraisal(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            emp = get_employee_by_user(request.user)
            if not emp:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
            forms = get_appraisal_forms(emp)
            return Response(AppraisalformSerializer(forms, many=True).data)
        except Exception as e:
            return _unexpected_error_response(e, "Appraisal GET failed")

    def post(self, request):
        try:
            form = srv_submit_appraisal(request.user, request.data)
            return Response(AppraisalformSerializer(form).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return _unexpected_error_response(e, "Appraisal POST failed")


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workflow_action(request):
    if request.method == 'GET':
        return Response(srv_get_runtime_records())
    try:
        result = srv_process_hr_workflow_action(
            request.user,
            request.data.get('action'),
            request.data.get('payload') or {},
        )
        return Response({"status": "success", **result})
    except PermissionDenied as e:
        return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValidationError as e:
        return Response({"error": _validation_error_message(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return _unexpected_error_response(e, "workflow_action failed")
