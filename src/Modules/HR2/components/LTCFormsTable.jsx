import { Card, Text, Table } from "@mantine/core";

export default function LTCFormsTable({ forms }) {
  return (
    <Card withBorder>
      <Text fw={600} mb="md">
        LTC Forms
      </Text>
      {!forms?.length ? (
        <Text c="dimmed">No LTC forms submitted yet.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Block Year</Table.Th>
              <Table.Th>Place of Visit</Table.Th>
              <Table.Th>Submission Date</Table.Th>
              <Table.Th>Status</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {forms.map((f) => (
              <Table.Tr key={f.id}>
                <Table.Td>{f.blockYear}</Table.Td>
                <Table.Td>{f.placeOfVisit || "-"}</Table.Td>
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
