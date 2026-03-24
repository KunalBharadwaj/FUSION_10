import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchLTCForms, submitLTCForm } from "./api";
import LTCFormsTable from "./components/LTCFormsTable";
import LTCApplyForm from "./components/LTCApplyForm";

const INITIAL_FORM = {
  blockYear: "",
  pfNo: 0,
  basicPaySalary: 0,
  departmentInfo: "",
  placeOfVisit: "",
  addressDuringLeave: "",
  modeofTravel: "",
  amountOfAdvanceRequired: 0,
  leaveRequired: false,
  leaveStartDate: "",
  leaveEndDate: "",
};

export default function LTC() {
  const [forms, setForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = () => {
    fetchLTCForms()
      .then((data) => setForms(Array.isArray(data) ? data : []))
      .catch((err) =>
        setError(
          err.response?.data?.error ||
            err.message ||
            "Failed to load LTC forms",
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
      await submitLTCForm(form);
      notifications.show({
        title: "Success",
        message: "LTC application submitted",
        color: "green",
      });
      setForm(INITIAL_FORM);
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.response?.data?.error || "Failed to submit LTC form",
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
          <Tabs.Tab value="apply">Apply LTC</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="applications" pt="md">
          <LTCFormsTable forms={forms} />
        </Tabs.Panel>
        <Tabs.Panel value="apply" pt="md">
          <LTCApplyForm
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
