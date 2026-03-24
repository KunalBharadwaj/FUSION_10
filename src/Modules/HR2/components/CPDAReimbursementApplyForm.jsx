import {
  Card,
  Stack,
  Group,
  Button,
  NumberInput,
  Textarea,
} from "@mantine/core";

export default function CPDAReimbursementApplyForm({
  form,
  setForm,
  onSubmit,
  submitting,
}) {
  return (
    <Card withBorder>
      <form onSubmit={onSubmit}>
        <Stack gap="md">
          <Group grow>
            <NumberInput
              label="PF Number"
              value={form.pfNo}
              onChange={(val) => setForm((f) => ({ ...f, pfNo: val ?? 0 }))}
              required
            />
            <NumberInput
              label="Advance Already Taken (₹)"
              value={form.advanceTaken}
              onChange={(val) =>
                setForm((f) => ({ ...f, advanceTaken: val ?? 0 }))
              }
              required
            />
          </Group>
          <Textarea
            label="Purpose"
            placeholder="Describe the purpose of reimbursement..."
            value={form.purpose}
            onChange={(e) =>
              setForm((f) => ({ ...f, purpose: e.target.value }))
            }
            required
          />
          <Button type="submit" loading={submitting}>
            Submit CPDA Reimbursement
          </Button>
        </Stack>
      </form>
    </Card>
  );
}
