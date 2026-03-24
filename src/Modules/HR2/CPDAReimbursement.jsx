import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  fetchCPDAReimbursementForms,
  submitCPDAReimbursementForm,
} from "./api";
import CPDAReimbursementTable from "./components/CPDAReimbursementTable";
import CPDAReimbursementApplyForm from "./components/CPDAReimbursementApplyForm";

const INITIAL_FORM = {
  pfNo: 0,
  advanceTaken: 0,
  purpose: "",
};

export default function CPDAReimbursement() {
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = () => {
    fetchCPDAReimbursementForms()
      .then((data) => setForms(Array.isArray(data) ? data : []))
      .catch((err) =>
        setError(
          err.response?.data?.error || err.message || "Failed to load forms",
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
      await submitCPDAReimbursementForm(form);
      notifications.show({
        title: "Success",
        message: "CPDA Reimbursement application submitted",
        color: "green",
      });
      setForm(INITIAL_FORM);
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message:
          err.response?.data?.error ||
          "Failed to submit CPDA Reimbursement form",
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
          <Tabs.Tab value="apply">Apply CPDA Reimbursement</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="applications" pt="md">
          <CPDAReimbursementTable forms={forms} />
        </Tabs.Panel>
        <Tabs.Panel value="apply" pt="md">
          <CPDAReimbursementApplyForm
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
