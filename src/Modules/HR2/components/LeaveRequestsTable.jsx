import { Card, Text, Table, Button } from "@mantine/core";
import { useState } from "react";
import { notifications } from "@mantine/notifications";
import { runWorkflowAction } from "../api";

export default function LeaveRequestsTable({ requests, onRefresh }) {
  const [loadingId, setLoadingId] = useState(null);

  const handleWithdraw = async (formId) => {
    setLoadingId(formId);
    try {
      await runWorkflowAction("withdraw_request", { form_id: formId });
      notifications.show({
        title: "Success",
        message: "Leave application withdrawn successfully",
        color: "green",
      });
      if (onRefresh) onRefresh();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.message || "Failed to withdraw leave request",
        color: "red",
      });
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <Card withBorder>
      <Text fw={600} mb="sm">
        My Leave Requests
      </Text>
      {!requests?.length ? (
        <Text c="dimmed">No leave requests yet.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Nature</Table.Th>
              <Table.Th>Start</Table.Th>
              <Table.Th>End</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {requests.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.natureOfLeave}</Table.Td>
                <Table.Td>{r.leaveStartDate}</Table.Td>
                <Table.Td>{r.leaveEndDate}</Table.Td>
                <Table.Td>{r.status}</Table.Td>
                <Table.Td>
                  {r.status === "PENDING" && (
                    <Button
                      size="compact-xs"
                      color="red"
                      variant="outline"
                      loading={loadingId === r.id}
                      onClick={() => handleWithdraw(r.id)}
                    >
                      Withdraw
                    </Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Card>
  );
}
