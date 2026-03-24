import { useState, useEffect } from "react";
import { Box, Loader, Alert } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchLeaveInbox, handleLeaveFile, searchEmployees } from "./api";
import LeaveInboxTable from "./components/LeaveInboxTable";
import HandleLeaveModal from "./components/HandleLeaveModal";

export default function LeaveInbox() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [action, setAction] = useState("ACCEPT");
  const [remarks, setRemarks] = useState("");
  const [forwardTo, setForwardTo] = useState("");
  const [employees, setEmployees] = useState([]);
  const [searchQ, setSearchQ] = useState("");
  const [processing, setProcessing] = useState(false);

  const loadData = async () => {
    try {
      setError(null);
      const data = await fetchLeaveInbox();
      setItems(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          err.message ||
          "Failed to load leave inbox",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const searchEmp = async () => {
    if (!searchQ.trim()) return;
    try {
      const res = await searchEmployees(searchQ);
      setEmployees(res || []);
    } catch {
      setEmployees([]);
    }
  };

  const handleAction = async () => {
    if (!selected) return;
    setProcessing(true);
    try {
      const payload = { action, remarks };
      if (action === "FORWARD") payload.forward_to = forwardTo;
      await handleLeaveFile(selected.id, payload);
      notifications.show({
        title: "Success",
        message: "Leave request processed",
        color: "green",
      });
      setModalOpen(false);
      setSelected(null);
      setRemarks("");
      setForwardTo("");
      loadData();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.response?.data?.error || "Failed to process",
        color: "red",
      });
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <Loader size="md" />;
  if (error) return <Alert color="red">{error}</Alert>;

  return (
    <Box p="md">
      <LeaveInboxTable
        items={items}
        onHandle={(item) => {
          setSelected(item);
          setModalOpen(true);
        }}
      />
      <HandleLeaveModal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        action={action}
        setAction={setAction}
        remarks={remarks}
        setRemarks={setRemarks}
        forwardTo={forwardTo}
        setForwardTo={setForwardTo}
        searchQ={searchQ}
        setSearchQ={setSearchQ}
        onSearch={searchEmp}
        employees={employees}
        onSubmit={handleAction}
        processing={processing}
      />
    </Box>
  );
}
