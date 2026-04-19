import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useSelector } from "react-redux";
import { fetchAppraisalForms, submitAppraisalForm, fetchAppraisalInbox } from "./api";
import AppraisalTable from "./components/AppraisalTable";
import AppraisalApplyForm from "./components/AppraisalApplyForm";
import WorkflowInboxTable from "./components/WorkflowInboxTable";

const APPLY_ROLES = [
  "faculty", "staff", "Professor", "Assistant Professor", "Associate Professor",
  "Employee", "Dean Academic", "HOD", "acadadmin", "studentacadadmin",
];
const APPROVAL_ROLES = [
  "HOD", "Director", "Registrar", "HR Admin", "HR Administrator", "Accountant", "Finance",
];

const INITIAL_FORM = {
  disciplineInfo: "",
  specificFieldOfKnowledge: "",
  currentResearchInterests: "",
  performanceComments: "",
};

export default function Appraisal() {
  const userRole = useSelector((state) => state.user.role);
  const canApply = APPLY_ROLES.includes(userRole);
  const canApprove = APPROVAL_ROLES.includes(userRole);

  const [forms, setForms] = useState([]);
  const [inboxForms, setInboxForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = () => {
    setLoading(true);
    const calls = [];
    if (canApply) calls.push(fetchAppraisalForms());
    if (canApprove) calls.push(fetchAppraisalInbox());

    Promise.all(calls)
      .then((results) => {
        if (canApply && canApprove) {
          setForms(Array.isArray(results[0]) ? results[0] : []);
          setInboxForms(Array.isArray(results[1]) ? results[1] : []);
        } else if (canApply) {
          setForms(Array.isArray(results[0]) ? results[0] : []);
        } else if (canApprove) {
          setInboxForms(Array.isArray(results[0]) ? results[0] : []);
        }
      })
      .catch((err) => setError(err.message || "Failed to load appraisal forms"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitAppraisalForm(form);
      notifications.show({
        title: "Success",
        message: "Appraisal form submitted",
        color: "green",
      });
      setForm(INITIAL_FORM);
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.message || "Failed to submit appraisal form",
        color: "red",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader size="md" />;
  if (error) return <Alert color="red">{error}</Alert>;

  const defaultTab = canApply ? "applications" : "inbox";

  return (
    <Box p="md">
      <Tabs defaultValue={defaultTab}>
        <Tabs.List>
          {canApply && <Tabs.Tab value="applications">My Applications</Tabs.Tab>}
          {canApply && <Tabs.Tab value="apply">Submit Appraisal</Tabs.Tab>}
          {canApprove && <Tabs.Tab value="inbox">Inbox</Tabs.Tab>}
        </Tabs.List>
        {canApply && (
          <Tabs.Panel value="applications" pt="md">
            <AppraisalTable forms={forms} />
          </Tabs.Panel>
        )}
        {canApply && (
          <Tabs.Panel value="apply" pt="md">
            <AppraisalApplyForm
              form={form}
              setForm={setForm}
              onSubmit={handleSubmit}
              submitting={submitting}
            />
          </Tabs.Panel>
        )}
        {canApprove && (
          <Tabs.Panel value="inbox" pt="md">
            <WorkflowInboxTable
              items={inboxForms}
              title="Appraisal Inbox"
              targetType="appraisal"
              onActionComplete={loadData}
            />
          </Tabs.Panel>
        )}
      </Tabs>
    </Box>
  );
}
