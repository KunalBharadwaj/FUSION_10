import {
  Card,
  Stack,
  Group,
  Button,
  TextInput,
  Textarea,
  NumberInput,
  Select,
  Checkbox,
} from "@mantine/core";

export default function LTCApplyForm({ form, setForm, onSubmit, submitting }) {
  return (
    <Card withBorder>
      <form onSubmit={onSubmit}>
        <Stack gap="md">
          <Group grow>
            <TextInput
              label="Block Year (e.g. 2024-2026)"
              placeholder="2024-2026"
              value={form.blockYear}
              onChange={(e) =>
                setForm((f) => ({ ...f, blockYear: e.target.value }))
              }
              required
            />
            <NumberInput
              label="PF Number"
              value={form.pfNo}
              onChange={(val) => setForm((f) => ({ ...f, pfNo: val ?? 0 }))}
              required
            />
          </Group>
          <Group grow>
            <NumberInput
              label="Basic Pay / Salary"
              value={form.basicPaySalary}
              onChange={(val) =>
                setForm((f) => ({ ...f, basicPaySalary: val ?? 0 }))
              }
            />
            <TextInput
              label="Department"
              value={form.departmentInfo}
              onChange={(e) =>
                setForm((f) => ({ ...f, departmentInfo: e.target.value }))
              }
            />
          </Group>
          <Group grow>
            <TextInput
              label="Place of Visit"
              value={form.placeOfVisit}
              onChange={(e) =>
                setForm((f) => ({ ...f, placeOfVisit: e.target.value }))
              }
            />
            <Select
              label="Mode of Travel"
              data={["Train", "Bus", "Air", "Own Vehicle", "Other"]}
              value={form.modeofTravel}
              onChange={(val) =>
                setForm((f) => ({ ...f, modeofTravel: val ?? "" }))
              }
              clearable
            />
          </Group>
          <Textarea
            label="Address During Leave"
            value={form.addressDuringLeave}
            onChange={(e) =>
              setForm((f) => ({ ...f, addressDuringLeave: e.target.value }))
            }
          />
          <NumberInput
            label="Amount of Advance Required (₹)"
            value={form.amountOfAdvanceRequired}
            onChange={(val) =>
              setForm((f) => ({ ...f, amountOfAdvanceRequired: val ?? 0 }))
            }
          />
          <Checkbox
            label="Leave Required?"
            checked={form.leaveRequired}
            onChange={(e) =>
              setForm((f) => ({ ...f, leaveRequired: e.currentTarget.checked }))
            }
          />
          {form.leaveRequired && (
            <Group grow>
              <TextInput
                type="date"
                label="Leave Start Date"
                value={form.leaveStartDate}
                onChange={(e) =>
                  setForm((f) => ({ ...f, leaveStartDate: e.target.value }))
                }
              />
              <TextInput
                type="date"
                label="Leave End Date"
                value={form.leaveEndDate}
                onChange={(e) =>
                  setForm((f) => ({ ...f, leaveEndDate: e.target.value }))
                }
              />
            </Group>
          )}
          <Button type="submit" loading={submitting}>
            Submit LTC Application
          </Button>
        </Stack>
      </form>
    </Card>
  );
}
