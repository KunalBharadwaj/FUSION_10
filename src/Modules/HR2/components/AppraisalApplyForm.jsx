import { Card, Stack, Button, TextInput, Textarea, Alert } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";

export default function AppraisalApplyForm({
  form,
  setForm,
  onSubmit,
  submitting,
}) {
  const now = new Date();
  const isWindowOpen = now.getMonth() === 0 || now.getMonth() === 1; // January (0) or February (1)

  return (
    <Card withBorder>
      {!isWindowOpen && (
        <Alert icon={<IconInfoCircle size={16} />} color="yellow" mb="md">
          Appraisal submissions are only accepted between January 1 – February
          28. You may fill out the form, but submission may be rejected by the
          server outside this window.
        </Alert>
      )}
      <form onSubmit={onSubmit}>
        <Stack gap="md">
          <TextInput
            label="Discipline / Department Info"
            value={form.disciplineInfo}
            onChange={(e) =>
              setForm((f) => ({ ...f, disciplineInfo: e.target.value }))
            }
          />
          <Textarea
            label="Specific Field of Knowledge"
            value={form.specificFieldOfKnowledge}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                specificFieldOfKnowledge: e.target.value,
              }))
            }
          />
          <Textarea
            label="Current Research Interests"
            value={form.currentResearchInterests}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                currentResearchInterests: e.target.value,
              }))
            }
          />
          <Textarea
            label="Performance Comments"
            value={form.performanceComments}
            onChange={(e) =>
              setForm((f) => ({ ...f, performanceComments: e.target.value }))
            }
          />
          <Button type="submit" loading={submitting}>
            Submit Appraisal
          </Button>
        </Stack>
      </form>
    </Card>
  );
}
