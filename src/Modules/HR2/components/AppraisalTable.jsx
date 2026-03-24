import { Card, Text, Table } from "@mantine/core";

export default function AppraisalTable({ forms }) {
  return (
    <Card withBorder>
      <Text fw={600} mb="md">
        Appraisal Forms
      </Text>
      {!forms?.length ? (
        <Text c="dimmed">No appraisal forms submitted yet.</Text>
      ) : (
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Year</Table.Th>
              <Table.Th>Discipline</Table.Th>
              <Table.Th>Submission Date</Table.Th>
              <Table.Th>Status</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {forms.map((f) => (
              <Table.Tr key={f.id}>
                <Table.Td>
                  {f.submissionDate
                    ? new Date(f.submissionDate).getFullYear()
                    : "-"}
                </Table.Td>
                <Table.Td>{f.disciplineInfo || "-"}</Table.Td>
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
