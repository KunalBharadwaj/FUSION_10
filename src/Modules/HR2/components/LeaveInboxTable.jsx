import { Card, Text, Table, Button } from "@mantine/core";

export default function LeaveInboxTable({ items, onHandle }) {
  return (
    <Card withBorder>
      <Text fw={600} mb="md">
        Leave Inbox
      </Text>
      {!items?.length ? (
        <Text c="dimmed">No pending leave requests in your inbox.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Name</Table.Th>
              <Table.Th>Designation</Table.Th>
              <Table.Th>Nature</Table.Th>
              <Table.Th>Start</Table.Th>
              <Table.Th>End</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.map((item) => (
              <Table.Tr key={item.id}>
                <Table.Td>{item.name}</Table.Td>
                <Table.Td>{item.designation}</Table.Td>
                <Table.Td>{item.natureOfLeave}</Table.Td>
                <Table.Td>{item.leaveStartDate}</Table.Td>
                <Table.Td>{item.leaveEndDate}</Table.Td>
                <Table.Td>{item.status}</Table.Td>
                <Table.Td>
                  <Button
                    size="xs"
                    variant="light"
                    onClick={() => onHandle(item)}
                  >
                    Handle
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Card>
  );
}
