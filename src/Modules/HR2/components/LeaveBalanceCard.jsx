import { Card, Text, Group } from "@mantine/core";

export default function LeaveBalanceCard({ balance }) {
  return (
    <Card withBorder>
      <Text fw={600} mb="sm">
        Leave Balance
      </Text>
      <Group gap="xl">
        <Text size="sm">Casual Leave: {balance?.casualLeave ?? "-"}</Text>
        <Text size="sm">
          Special Casual: {balance?.specialCasualLeave ?? "-"}
        </Text>
        <Text size="sm">Earned Leave: {balance?.earnedLeave ?? "-"}</Text>
        <Text size="sm">Commuted: {balance?.commutedLeave ?? "-"}</Text>
        <Text size="sm">
          Restricted Holiday: {balance?.restrictedHoliday ?? "-"}
        </Text>
        <Text size="sm">Station Leave: {balance?.stationLeave ?? "-"}</Text>
        <Text size="sm">Vacation: {balance?.vacationLeave ?? "-"}</Text>
      </Group>
    </Card>
  );
}
