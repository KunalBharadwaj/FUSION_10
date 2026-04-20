import { Modal, Select, Textarea, TextInput, Button } from "@mantine/core";

export default function HandleLeaveModal({
  opened,
  onClose,
  action,
  setAction,
  remarks,
  setRemarks,
  forwardTo,
  setForwardTo,
  searchQ,
  setSearchQ,
  onSearch,
  employees,
  onSubmit,
  processing,
}) {
  return (
    <Modal opened={opened} onClose={onClose} title="Handle Leave Request">
      <Select
        label="Action"
        data={[
          { value: "ACCEPT", label: "Accept" },
          { value: "REJECT", label: "Reject" },
          { value: "FORWARD", label: "Forward" },
        ]}
        value={action}
        onChange={(v) => setAction(v || "ACCEPT")}
      />
      <Textarea
        label="Remarks"
        value={remarks}
        onChange={(e) => setRemarks(e.target.value)}
        placeholder="Optional remarks"
        mt="sm"
      />
      {action === "FORWARD" && (
        <>
          <TextInput
            label="Search Employee (username)"
            value={searchQ}
            onChange={(e) => setSearchQ(e.target.value)}
            onBlur={onSearch}
            mt="sm"
          />
          <Select
            label="Forward To"
            data={employees.map((e) => ({
              value: e.username,
              label: `${`${e.first_name} ${e.last_name}`.trim() || e.username} (${e.username})`,
            }))}
            value={forwardTo}
            onChange={setForwardTo}
            mt="sm"
            searchable
          />
        </>
      )}
      <Button fullWidth mt="md" onClick={onSubmit} loading={processing}>
        Submit
      </Button>
    </Modal>
  );
}
