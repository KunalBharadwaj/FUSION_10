import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchCPDAAdvanceForms, submitCPDAAdvanceForm } from "./api";
import CPDAAdvanceTable from "./components/CPDAAdvanceTable";
import CPDAAdvanceApplyForm from "./components/CPDAAdvanceApplyForm";

const INITIAL_FORM = {
  pfNo: 0,
  purpose: "",
  amountRequired: 0,
};

export default function CPDAAdvance() {
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = () => {
    fetchCPDAAdvanceForms()
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
      await submitCPDAAdvanceForm(form);
      notifications.show({
        title: "Success",
        message: "CPDA Advance application submitted",
        color: "green",
      });
      setForm(INITIAL_FORM);
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message:
          err.response?.data?.error || "Failed to submit CPDA Advance form",
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
          <Tabs.Tab value="apply">Apply CPDA Advance</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="applications" pt="md">
          <CPDAAdvanceTable forms={forms} />
        </Tabs.Panel>
        <Tabs.Panel value="apply" pt="md">
          <CPDAAdvanceApplyForm
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
