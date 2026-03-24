import axios from "axios";
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
} from "../../routes/hr2Routes";

const getAuthHeaders = () => {
  const token = localStorage.getItem("authToken");
  if (!token) throw new Error("Authorization token not found");
  return { Authorization: `Token ${token}` };
};

export const fetchLeaveBalance = async () => {
  const { data } = await axios.get(leaveBalanceRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const submitLeaveForm = async (formData) => {
  const { data } = await axios.post(submitLeaveRoute, formData, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};

export const fetchLeaveRequests = async () => {
  const { data } = await axios.get(leaveRequestsRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const fetchLeaveInbox = async () => {
  const { data } = await axios.get(leaveInboxRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const handleLeaveFile = async (id, payload) => {
  const { data } = await axios.post(handleLeaveFileRoute(id), payload, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};

export const searchEmployees = async (query) => {
  const { data } = await axios.get(searchEmployeesRoute, {
    params: { q: query },
    headers: getAuthHeaders(),
  });
  return data;
};

export const fetchLTCForms = async () => {
  const { data } = await axios.get(ltcRoute, { headers: getAuthHeaders() });
  return data;
};

export const fetchCPDAAdvanceForms = async () => {
  const { data } = await axios.get(cpdaAdvanceRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const fetchCPDAReimbursementForms = async () => {
  const { data } = await axios.get(cpdaReimbursementRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const fetchAppraisalForms = async () => {
  const { data } = await axios.get(appraisalRoute, {
    headers: getAuthHeaders(),
  });
  return data;
};

export const submitLTCForm = async (formData) => {
  const { data } = await axios.post(ltcRoute, formData, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};

export const submitCPDAAdvanceForm = async (formData) => {
  const { data } = await axios.post(cpdaAdvanceRoute, formData, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};

export const submitCPDAReimbursementForm = async (formData) => {
  const { data } = await axios.post(cpdaReimbursementRoute, formData, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};

export const submitAppraisalForm = async (formData) => {
  const { data } = await axios.post(appraisalRoute, formData, {
    headers: { ...getAuthHeaders(), "Content-Type": "application/json" },
  });
  return data;
};
