import { Box, Text, Stack } from "@mantine/core";

export default function HRAccessInfo() {
  return (
    <Box p="xl">
      <Stack gap="md">
        <Text size="lg" fw={600}>
          HR Module Access
        </Text>
        <Text c="dimmed" size="sm">
          The Human Resource (HR) module is available for faculty and staff
          members. It includes leave management, LTC, CPDA
          advance/reimbursement, and appraisal forms.
        </Text>
        <Text c="dimmed" size="sm">
          If you are a faculty or staff member and need access, please contact
          the administration.
        </Text>
      </Stack>
    </Box>
  );
}
