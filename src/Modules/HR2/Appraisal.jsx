import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchAppraisalForms, submitAppraisalForm } from "./api";
import AppraisalTable from "./components/AppraisalTable";
import AppraisalApplyForm from "./components/AppraisalApplyForm";

const INITIAL_FORM = {
  disciplineInfo: "",
  specificFieldOfKnowledge: "",
  currentResearchInterests: "",
  performanceComments: "",
};

export default function Appraisal() {
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = () => {
    fetchAppraisalForms()
      .then((data) => setForms(Array.isArray(data) ? data : []))
      .catch((err) =>
        setError(
          err.response?.data?.error ||
            err.message ||
            "Failed to load appraisal forms",
        ),
      )
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
        message: err.response?.data?.error || "Failed to submit appraisal form",
        color: "red",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader size="md" />;
  if (error) return <Alert color="red">{error}</Alert>;

  return (
    <Box p="md">
      <Tabs defaultValue="applications">
        <Tabs.List>
          <Tabs.Tab value="applications">My Applications</Tabs.Tab>
          <Tabs.Tab value="apply">Submit Appraisal</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="applications" pt="md">
          <AppraisalTable forms={forms} />
        </Tabs.Panel>
        <Tabs.Panel value="apply" pt="md">
          <AppraisalApplyForm
            form={form}
            setForm={setForm}
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        </Tabs.Panel>
      </Tabs>
    </Box>
  );
}
