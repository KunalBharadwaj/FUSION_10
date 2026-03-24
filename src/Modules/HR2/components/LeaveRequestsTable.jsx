import { Card, Text, Table } from "@mantine/core";

export default function LeaveRequestsTable({ requests }) {
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
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {requests.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.natureOfLeave}</Table.Td>
                <Table.Td>{r.leaveStartDate}</Table.Td>
                <Table.Td>{r.leaveEndDate}</Table.Td>
                <Table.Td>{r.status}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Card>
  );
}
