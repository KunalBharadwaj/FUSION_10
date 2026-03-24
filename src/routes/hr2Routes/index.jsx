import { host } from "../globalRoutes";

const hr2Base = `${host}/hr2/api`;

// Feature paths (frontend routes)
export const hr2LeavePath = "/hr2/leave";
export const hr2LeaveInboxPath = "/hr2/leave-inbox";
export const hr2LTCPath = "/hr2/ltc";
export const hr2CPDAAdvancePath = "/hr2/cpda-advance";
export const hr2CPDAReimbursementPath = "/hr2/cpda-reimbursement";
export const hr2AppraisalPath = "/hr2/appraisal";
export const hr2InfoPath = "/hr2/info";

// API routes (Backend selectors / services)
export const leaveBalanceRoute = `${hr2Base}/get_leave_balance/`;
export const submitLeaveRoute = `${hr2Base}/submit_leave_form/`;
export const leaveRequestsRoute = `${hr2Base}/get_leave_requests/`;
export const leaveInboxRoute = `${hr2Base}/get_leave_inbox/`;
export const handleLeaveFileRoute = (id) =>
  `${hr2Base}/handle_leave_file/${id}/`;
export const searchEmployeesRoute = `${hr2Base}/search_employees/`;
export const ltcRoute = `${hr2Base}/ltc/`;
export const cpdaAdvanceRoute = `${hr2Base}/cpdaadv/`;
export const cpdaReimbursementRoute = `${hr2Base}/cpdareim/`;
export const appraisalRoute = `${hr2Base}/appraisal/`;
