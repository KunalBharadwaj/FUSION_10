import { Card, Text, Table, Button, Group } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { useState } from "react";
import { runWorkflowAction } from "../api";

export default function WorkflowInboxTable({ items, title, targetType, onActionComplete }) {
  const [loadingId, setLoadingId] = useState(null);

  const handleAction = async (item, decision) => {
    setLoadingId(item.id);
    try {
      let actionName = "";
      if (item.status === "PENDING") {
        if (targetType === "cpda_advance" || targetType === "cpda_reimbursement") actionName = "verify_cpda_claim";
        else if (targetType === "ltc") actionName = "verify_ltc_claim";
        else if (targetType === "appraisal") actionName = "review_appraisal";
      } else if (item.status === "FORWARDED") {
        if (targetType === "cpda_advance" || targetType === "cpda_reimbursement") actionName = "cpda_decision";
        else if (targetType === "ltc") actionName = "ltc_decision";
        else if (targetType === "appraisal") actionName = "appraisal_decision";
      } else if (item.status === "APPROVED" && (targetType === "cpda_advance" || targetType === "cpda_reimbursement" || targetType === "ltc")) {
        actionName = "process_financial_claim";
      }

      await runWorkflowAction(actionName, {
        form_id: item.id,
        target_type: targetType,
        decision: decision,
        claim_type: targetType === "ltc" ? "LTC" : "CPDA"
      });

      notifications.show({
        title: "Success",
        message: `Form marked as ${decision}`,
        color: "green",
      });
      if (onActionComplete) onActionComplete();
    } catch (err) {
      notifications.show({
        title: "Error",
        message: err.message || "Failed to process workflow action",
        color: "red",
      });
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <Card withBorder>
      <Text fw={600} mb="md">
        {title}
      </Text>
      {!items?.length ? (
        <Text c="dimmed">No pending requests in your inbox.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Name</Table.Th>
              <Table.Th>Designation</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.map((item) => (
              <Table.Tr key={item.id}>
                <Table.Td>{item.id}</Table.Td>
                <Table.Td>{item.name}</Table.Td>
                <Table.Td>{item.designation}</Table.Td>
                <Table.Td>{item.status}</Table.Td>
                <Table.Td>
                  {item.status === "APPROVED" ? (
                    <Button
                      size="xs"
                      color="blue"
                      loading={loadingId === item.id}
                      onClick={() => handleAction(item, "PROCESSED")}
                    >
                      Process Fin. Claim
                    </Button>
                  ) : (
                    <Group gap="xs">
                      <Button
                        size="xs"
                        color="green"
                        loading={loadingId === item.id}
                        onClick={() => handleAction(item, "APPROVE")}
                      >
                        {item.status === "PENDING" ? "Verify/Forward" : "Approve"}
                      </Button>
                      <Button
                        size="xs"
                        color="red"
                        variant="outline"
                        loading={loadingId === item.id}
                        onClick={() => handleAction(item, "REJECT")}
                      >
                        Reject
                      </Button>
                    </Group>
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
