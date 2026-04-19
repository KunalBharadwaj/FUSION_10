import axios from "axios";
import { getApiErrorMessage } from "./utils/apiError";
import {
  leaveBalanceRoute,
  submitLeaveRoute,
  leaveRequestsRoute,
  leaveInboxRoute,
  handleLeaveFileRoute,
  searchEmployeesRoute,
  ltcRoute,
  cpdaAdvanceRoute,
  cpdaReimbursementRoute,
  appraisalRoute,
  workflowActionRoute,
} from "../../routes/hr2Routes";

const getAuthHeaders = () => {
  const token = localStorage.getItem("authToken");
  if (!token) throw new Error("Authorization token not found");
  return { Authorization: `Token ${token}` };
};

const withApiError = (error, fallbackMessage) => {
  const normalized = new Error(getApiErrorMessage(error, fallbackMessage));
  normalized.original = error;
  throw normalized;
};

export const fetchLeaveBalance = async () => {
  try {
    const { data } = await axios.get(leaveBalanceRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch leave balance.");
  }
};

export const submitLeaveForm = async (formData) => {
  try {
    const { data } = await axios.post(submitLeaveRoute, formData, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to submit leave request.");
  }
};

export const fetchLeaveRequests = async () => {
  try {
    const { data } = await axios.get(leaveRequestsRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch leave requests.");
  }
};

export const fetchLeaveInbox = async () => {
  try {
    const { data } = await axios.get(leaveInboxRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch leave inbox.");
  }
};

export const handleLeaveFile = async (id, payload) => {
  try {
    const { data } = await axios.post(handleLeaveFileRoute(id), payload, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to process leave action.");
  }
};

export const searchEmployees = async (query) => {
  try {
    const { data } = await axios.get(searchEmployeesRoute, {
      params: { q: query },
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to search employees.");
  }
};

export const fetchLTCForms = async () => {
  try {
    const { data } = await axios.get(ltcRoute, { headers: getAuthHeaders() });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch LTC forms.");
  }
};

export const fetchCPDAAdvanceForms = async () => {
  try {
    const { data } = await axios.get(cpdaAdvanceRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch CPDA advance forms.");
  }
};

export const fetchCPDAReimbursementForms = async () => {
  try {
    const { data } = await axios.get(cpdaReimbursementRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch CPDA reimbursement forms.");
  }
};

export const fetchAppraisalForms = async () => {
  try {
    const { data } = await axios.get(appraisalRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch appraisal forms.");
  }
};

export const submitLTCForm = async (formData) => {
  try {
    const { data } = await axios.post(ltcRoute, formData, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to submit LTC form.");
  }
};

export const submitCPDAAdvanceForm = async (formData) => {
  try {
    const { data } = await axios.post(cpdaAdvanceRoute, formData, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to submit CPDA advance form.");
  }
};

export const submitCPDAReimbursementForm = async (formData) => {
  try {
    const { data } = await axios.post(cpdaReimbursementRoute, formData, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to submit CPDA reimbursement form.");
  }
};

export const submitAppraisalForm = async (formData) => {
  try {
    const { data } = await axios.post(appraisalRoute, formData, {
      headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to submit appraisal form.");
  }
};

export const runWorkflowAction = async (action, payload = {}) => {
  try {
    const { data } = await axios.post(
      workflowActionRoute,
      { action, payload },
      { headers: { ...getAuthHeaders(), "Content-Type": "application/json" } },
    );
    return data;
  } catch (error) {
    withApiError(error, "Workflow action failed.");
  }
};

export const fetchWorkflowRecords = async () => {
  try {
    const { data } = await axios.get(workflowActionRoute, {
      headers: getAuthHeaders(),
    });
    return data;
  } catch (error) {
    withApiError(error, "Failed to fetch workflow records.");
  }
};
