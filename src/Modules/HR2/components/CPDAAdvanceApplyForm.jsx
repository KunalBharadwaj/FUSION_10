import {
  Card,
  Stack,
  Group,
  Button,
  NumberInput,
  Textarea,
} from "@mantine/core";

export default function CPDAAdvanceApplyForm({
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
              label="Amount Required (₹)"
              value={form.amountRequired}
              onChange={(val) =>
                setForm((f) => ({ ...f, amountRequired: val ?? 0 }))
              }
              required
            />
          </Group>
          <Textarea
            label="Purpose"
            placeholder="Describe the purpose of the CPDA advance..."
            value={form.purpose}
            onChange={(e) =>
              setForm((f) => ({ ...f, purpose: e.target.value }))
            }
            required
          />
          <Button type="submit" loading={submitting}>
            Submit CPDA Advance
          </Button>
        </Stack>
      </form>
    </Card>
  );
}
