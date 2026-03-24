import { useState, useEffect } from "react";
import { Box, Loader, Alert, Tabs } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchLeaveBalance, fetchLeaveRequests, submitLeaveForm } from "./api";
import LeaveBalanceCard from "./components/LeaveBalanceCard";
import LeaveApplyForm from "./components/LeaveApplyForm";
import LeaveRequestsTable from "./components/LeaveRequestsTable";

const INITIAL_FORM = {
  natureOfLeave: "",
  leaveStartDate: "",
  leaveEndDate: "",
  purposeOfLeave: "",
  addressDuringLeave: "",
  academicResponsibility: "",
  addministrativeResponsibiltyAssigned: "",
};

export default function Leave() {
  const [balance, setBalance] = useState(null);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(INITIAL_FORM);

  const loadData = async () => {
    try {
      setError(null);
      const [bal, reqs] = await Promise.all([
        fetchLeaveBalance(),
        fetchLeaveRequests(),
      ]);
      setBalance(bal);
      setRequests(Array.isArray(reqs) ? reqs : []);
    } catch (err) {
      setError(
        err.response?.data?.error || err.message || "Failed to load data",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await submitLeaveForm(form);
      notifications.show({
        title: "Success",
        message: "Leave request submitted",
        color: "green",
      });
      setForm(INITIAL_FORM);
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.response?.data?.error || "Failed to submit",
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
      <Tabs defaultValue="balance">
        <Tabs.List>
          <Tabs.Tab value="balance">Leave Balance</Tabs.Tab>
          <Tabs.Tab value="apply">Apply Leave</Tabs.Tab>
          <Tabs.Tab value="requests">My Requests</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="balance" pt="md">
          <LeaveBalanceCard balance={balance} />
        </Tabs.Panel>
        <Tabs.Panel value="apply" pt="md">
          <LeaveApplyForm
            form={form}
            setForm={setForm}
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        </Tabs.Panel>
        <Tabs.Panel value="requests" pt="md">
          <LeaveRequestsTable requests={requests} />
        </Tabs.Panel>
      </Tabs>
    </Box>
  );
}
