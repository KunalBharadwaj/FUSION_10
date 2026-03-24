import { Card, Text, Table } from "@mantine/core";

export default function CPDAAdvanceTable({ forms }) {
  return (
    <Card withBorder>
      <Text fw={600} mb="md">
        CPDA Advance Forms
      </Text>
      {!forms?.length ? (
        <Text c="dimmed">No CPDA advance forms submitted yet.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Purpose</Table.Th>
              <Table.Th>Amount</Table.Th>
              <Table.Th>Submission Date</Table.Th>
              <Table.Th>Status</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {forms.map((f) => (
              <Table.Tr key={f.id}>
                <Table.Td>{f.purpose || "-"}</Table.Td>
                <Table.Td>{f.amountRequired}</Table.Td>
                <Table.Td>{f.submissionDate}</Table.Td>
                <Table.Td>{f.status}</Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      )}
    </Card>
  );
}
