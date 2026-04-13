import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Code,
  Group,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  Textarea,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { fetchWorkflowRecords, runWorkflowAction } from "./api";

const ACTIONS = [
  { value: "nominate_substitute", label: "Nominate Substitute" },
  { value: "respond_substitute", label: "Respond Substitute" },
  { value: "modify_request", label: "Modify Request" },
  { value: "withdraw_request", label: "Withdraw Request" },
  { value: "acknowledge_withdrawal", label: "Acknowledge Withdrawal" },
  { value: "request_cancellation", label: "Request Cancellation" },
  { value: "cancellation_decision", label: "Cancellation Decision" },
  { value: "submit_extension", label: "Submit Extension" },
  { value: "submit_resumption", label: "Submit Resumption" },
  { value: "verify_resumption", label: "Verify Resumption" },
  { value: "hod_decision", label: "HoD Decision" },
  { value: "sanctioning_decision", label: "Sanctioning Decision" },
  { value: "review_appraisal", label: "Review Appraisal" },
  { value: "appraisal_decision", label: "Appraisal Decision" },
  { value: "verify_ltc_claim", label: "Verify LTC Claim" },
  { value: "ltc_decision", label: "LTC Decision" },
  { value: "verify_cpda_claim", label: "Verify CPDA Claim" },
  { value: "cpda_decision", label: "CPDA Decision" },
  { value: "process_financial_claim", label: "Process Financial Claim" },
  { value: "run_year_end_leave_closure", label: "Year End Leave Closure" },
  { value: "run_sla", label: "Run SLA Reminders" },
  { value: "maintain_policy", label: "Maintain Policy" },
  { value: "maintain_calendar", label: "Maintain Calendar" },
];

const PAYLOAD_PRESETS = {
  nominate_substitute: { substitute_username: "staff01" },
  respond_substitute: { decision: "ACCEPT", request_id: "REQ-001" },
  modify_request: { form_id: 1, purposeOfLeave: "Updated reason" },
  withdraw_request: { form_id: 1 },
  acknowledge_withdrawal: { form_id: 1 },
  request_cancellation: { form_id: 1 },
  cancellation_decision: { form_id: 1, decision: "APPROVE" },
  submit_extension: { form_id: 1, new_end_date: "2026-04-30" },
  submit_resumption: { form_id: 1, resumption_date: "2026-04-30" },
  verify_resumption: { form_id: 1 },
  hod_decision: {
    form_id: 1,
    decision: "APPROVE",
    remarks: "Approved after review",
  },
  sanctioning_decision: {
    form_id: 1,
    decision: "APPROVE",
    remarks: "Approved after review",
  },
  review_appraisal: { form_id: 1 },
  appraisal_decision: { form_id: 1, decision: "APPROVE" },
  verify_ltc_claim: { form_id: 1 },
  ltc_decision: { form_id: 1, decision: "APPROVE" },
  verify_cpda_claim: { form_id: 1, target_type: "cpda_advance" },
  cpda_decision: {
    form_id: 1,
    target_type: "cpda_advance",
    decision: "APPROVE",
  },
  process_financial_claim: { form_id: 1, claim_type: "CPDA" },
  run_year_end_leave_closure: {},
  run_sla: { assignee: "hradmin01" },
  maintain_policy: { parameters: { published: true, casual_leave: 8 } },
  maintain_calendar: { entry: { date: "2026-04-30", type: "RH" } },
};

const formatJson = (value) => JSON.stringify(value, null, 2);

export default function WorkflowActions() {
  const [action, setAction] = useState("run_sla");
  const [payloadText, setPayloadText] = useState(
    formatJson(PAYLOAD_PRESETS.run_sla),
  );
  const [records, setRecords] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const auditRows = useMemo(() => records?.audit_log || [], [records]);
  const notificationRows = useMemo(
    () => records?.notifications || [],
    [records],
  );
  const financeRows = useMemo(() => records?.finance_handoffs || [], [records]);

  const loadRecords = async () => {
    try {
      setError("");
      const data = await fetchWorkflowRecords();
      setRecords(data);
    } catch (err) {
      setError(
        err.response?.data?.error || err.message || "Unable to load HR records",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecords();
  }, []);

  const handleActionChange = (value) => {
    const nextAction = value || "run_sla";
    setAction(nextAction);
    setPayloadText(formatJson(PAYLOAD_PRESETS[nextAction] || {}));
    setError("");
    setResult(null);
  };

  const submit = async () => {
    let payload;
    try {
      payload = payloadText.trim() ? JSON.parse(payloadText) : {};
    } catch {
      setError("Payload must be valid JSON.");
      return;
    }

    setRunning(true);
    try {
      setError("");
      const data = await runWorkflowAction(action, payload);
      setResult(data);
      notifications.show({
        title: "Done",
        message: data.state || "Action recorded",
        color: "green",
      });
      await loadRecords();
    } catch (err) {
      const message =
        err.response?.data?.error || err.message || "Action failed";
      setError(message);
      notifications.show({ title: "Action failed", message, color: "red" });
    } finally {
      setRunning(false);
    }
  };

  return (
    <Box p="md">
      <Stack gap="md">
        <Title order={2}>Workflow Actions</Title>
        {error && <Alert color="red">{error}</Alert>}
        <Paper withBorder p="md" radius="sm">
          <Stack gap="md">
            <Select
              label="Action"
              data={ACTIONS}
              value={action}
              onChange={handleActionChange}
              searchable
            />
            <Textarea
              label="Payload"
              minRows={8}
              autosize
              value={payloadText}
              onChange={(event) => setPayloadText(event.currentTarget.value)}
            />
            <Group justify="space-between">
              <Button variant="outline" onClick={loadRecords} loading={loading}>
                Refresh Records
              </Button>
              <Button onClick={submit} loading={running}>
                Run Action
              </Button>
            </Group>
          </Stack>
        </Paper>

        {result && (
          <Paper withBorder p="md" radius="sm">
            <Text fw={600} mb="xs">
              Latest Result
            </Text>
            <Code block>{formatJson(result)}</Code>
          </Paper>
        )}

        <Paper withBorder p="md" radius="sm">
          <Text fw={600} mb="sm">
            Audit History
          </Text>
          <Table striped highlightOnHover withTableBorder>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Time</Table.Th>
                <Table.Th>User</Table.Th>
                <Table.Th>Action</Table.Th>
                <Table.Th>Target</Table.Th>
                <Table.Th>Status</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {auditRows.length === 0 ? (
                <Table.Tr>
                  <Table.Td colSpan={5}>No audit records yet.</Table.Td>
                </Table.Tr>
              ) : (
                auditRows.map((item, index) => (
                  <Table.Tr key={`${item.timestamp}-${item.action}-${index}`}>
                    <Table.Td>{item.timestamp}</Table.Td>
                    <Table.Td>{item.user}</Table.Td>
                    <Table.Td>{item.action}</Table.Td>
                    <Table.Td>{`${item.target_type || ""} ${item.target_id || ""}`}</Table.Td>
                    <Table.Td>{item.status}</Table.Td>
                  </Table.Tr>
                ))
              )}
            </Table.Tbody>
          </Table>
        </Paper>

        <Paper withBorder p="md" radius="sm">
          <Text fw={600} mb="sm">
            Notifications And Finance
          </Text>
          <Code block>
            {formatJson({
              notifications: notificationRows,
              finance_handoffs: financeRows,
              policy: records?.policy || {},
              calendar: records?.calendar || [],
            })}
          </Code>
        </Paper>
      </Stack>
    </Box>
  );
}
