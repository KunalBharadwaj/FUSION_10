import { useEffect, useState } from "react";
import {
  Card,
  Stack,
  Group,
  Button,
  TextInput,
  Textarea,
  Select,
} from "@mantine/core";
import { searchEmployees } from "../api";

export default function LeaveApplyForm({
  form,
  setForm,
  onSubmit,
  submitting,
}) {
  const [employeeOptions, setEmployeeOptions] = useState([]);

  useEffect(() => {
    searchEmployees("")
      .then((data) => {
        setEmployeeOptions(
          data.map((emp) => ({
            value: emp.username,
            label: `${emp.first_name} ${emp.last_name}`.trim() || emp.username,
          })),
        );
      })
      .catch(() => {});
  }, []);

  return (
    <Card withBorder>
      <form onSubmit={onSubmit}>
        <Stack gap="md">
          <Select
            label="Nature of Leave"
            data={[
              { value: "casual_leave", label: "Casual Leave" },
              { value: "earned_leave", label: "Earned Leave" },
              { value: "special_casual_leave", label: "Special Casual Leave" },
              { value: "restricted_holiday", label: "Restricted Holiday" },
              { value: "commuted_leave", label: "Commuted Leave" },
              { value: "vacation_leave", label: "Vacation Leave" },
            ]}
            value={form.natureOfLeave}
            onChange={(val) =>
              setForm((f) => ({ ...f, natureOfLeave: val ?? "" }))
            }
            placeholder="Select leave type"
            required
          />
          <Group grow>
            <TextInput
              type="date"
              label="Start Date"
              value={form.leaveStartDate}
              onChange={(e) =>
                setForm((f) => ({ ...f, leaveStartDate: e.target.value }))
              }
              required
            />
            <TextInput
              type="date"
              label="End Date"
              value={form.leaveEndDate}
              onChange={(e) =>
                setForm((f) => ({ ...f, leaveEndDate: e.target.value }))
              }
              required
            />
          </Group>
          <Textarea
            label="Purpose of Leave"
            value={form.purposeOfLeave}
            onChange={(e) =>
              setForm((f) => ({ ...f, purposeOfLeave: e.target.value }))
            }
          />
          <Textarea
            label="Address During Leave"
            value={form.addressDuringLeave}
            onChange={(e) =>
              setForm((f) => ({ ...f, addressDuringLeave: e.target.value }))
            }
          />
          <Select
            label="Academic Responsibility"
            data={employeeOptions}
            value={form.academicResponsibility}
            onChange={(val) =>
              setForm((f) => ({ ...f, academicResponsibility: val ?? "" }))
            }
            searchable
            clearable
            placeholder="Select faculty"
          />
          <Select
            label="Administrative Responsibility Assigned"
            data={employeeOptions}
            value={form.addministrativeResponsibiltyAssigned}
            onChange={(val) =>
              setForm((f) => ({
                ...f,
                addministrativeResponsibiltyAssigned: val ?? "",
              }))
            }
            searchable
            clearable
            placeholder="Select faculty"
          />
          <Button type="submit" loading={submitting}>
            Submit
          </Button>
        </Stack>
      </form>
    </Card>
  );
}
