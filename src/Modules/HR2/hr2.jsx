import { Routes, Route, Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { useState, useEffect } from "react";
import { Layout } from "../../components/layout";
import Nav from "./components/Nav";
import Leave from "./Leave";
import LeaveInbox from "./LeaveInbox";
import LTC from "./LTC";
import CPDAAdvance from "./CPDAAdvance";
import CPDAReimbursement from "./CPDAReimbursement";
import Appraisal from "./Appraisal";
import WorkflowActions from "./WorkflowActions";
import HRAccessInfo from "./components/HRAccessInfo";
import ProtectedRoute from "./routes/protectedRoutes";

// All roles that can access the HR2 module
const HR_ROLES = [
  // Faculty / Employee submitter roles
  "faculty",
  "staff",
  "Professor",
  "Assistant Professor",
  "Associate Professor",
  "Employee",
  "Dean Academic",
  "acadadmin",
  "studentacadadmin",
  // Approval / management roles
  "HOD",
  "Director",
  "Registrar",
  "HR Admin",
  "HR Administrator",
  "Accountant",
  "Finance",
];

// Roles that can SUBMIT new forms
export const APPLY_ROLES = [
  "faculty",
  "staff",
  "Professor",
  "Assistant Professor",
  "Associate Professor",
  "Employee",
  "Dean Academic",
  "HOD",
  "acadadmin",
  "studentacadadmin",
];

// Roles that APPROVE / process forms from the Inbox
export const APPROVAL_ROLES = [
  "HOD",
  "Director",
  "Registrar",
  "HR Admin",
  "HR Administrator",
  "Accountant",
  "Finance",
];

export default function HR2() {
  const userRole = useSelector((state) => state.user.role);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (userRole !== undefined && userRole !== null) {
      setIsLoaded(true);
    }
  }, [userRole]);

  if (!isLoaded) return null;

  const hasHRAccess = HR_ROLES.includes(userRole);

  const defaultRedirectPath = () => {
    if (!hasHRAccess) return "/hr2/info";
    // Approval-only roles go straight to CPDA Advance Inbox
    if (APPROVAL_ROLES.includes(userRole) && !APPLY_ROLES.includes(userRole)) {
      return "/hr2/cpda-advance";
    }
    return "/hr2/leave";
  };

  return (
    <Layout>
      {hasHRAccess && <Nav />}
      <Routes>
        <Route
          path="/"
          element={<Navigate to={defaultRedirectPath()} replace />}
        />
        <Route path="/info" element={<HRAccessInfo />} />
        <Route
          path="/leave"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <Leave />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leave-inbox"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <LeaveInbox />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ltc"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <LTC />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cpda-advance"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <CPDAAdvance />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cpda-reimbursement"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <CPDAReimbursement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/appraisal"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <Appraisal />
            </ProtectedRoute>
          }
        />
        <Route
          path="/workflow-actions"
          element={
            <ProtectedRoute roles={HR_ROLES}>
              <WorkflowActions />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}
