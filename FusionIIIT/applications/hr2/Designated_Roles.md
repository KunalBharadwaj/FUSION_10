# Module Name: HR2

## Designated User Roles & Permissions

### 1. Role Name: HR Module Admin

* **Description:** Primary manager for HR2 configuration, workflow oversight, and records administration.

* **Permissions:**

  * Full CRUD (Create, Read, Update, Delete) operations on HR2 module data.

  * Manage leave, LTC, CPDA, appraisal, and workflow records.

  * Review, route, and close workflow actions where required.

  * Access audit logs, notifications, and reporting tools.

  * Configure module-level policies, calendars, and year-end actions.

  * Maintain leave policy parameters and holiday/RH calendar records.

### 2. Role Name: Employee / Faculty / Staff Member

* **Description:** Standard operational user who submits and manages personal HR requests.

* **Permissions:**

  * View personal HR records, balances, and application status.

  * Create and submit leave, LTC, CPDA, and appraisal requests.

  * Edit own draft requests before final submission.

  * Respond to workflow actions when a request is returned or forwarded.

  * View individual summaries, balances, and attached documents.

  * Request substitute nomination, withdrawal, cancellation, extension, and resumption where applicable.

### 3. Role Name: Reviewer / HoD

* **Description:** Supervisory user who reviews employee-submitted requests and provides the HoD-level decision where applicable.

* **Permissions:**

  * Read assigned or forwarded HR requests.

  * Review, approve, reject, forward, or request modification of submissions.

  * Add remarks and decision notes to workflow actions.

  * Access pending inbox items and summary views for oversight.

  * Handle HoD decision flows for leave, appraisal, LTC, and CPDA items where assigned.

  * Cannot modify unrelated users' records outside the assigned approval flow.

### 4. Role Name: Sanctioning Authority / Director / Registrar

* **Description:** Higher-level authority that finalizes routed requests requiring sanction beyond HoD review.

* **Permissions:**

  * Read routed leave, appraisal, LTC, and CPDA requests.

  * Approve or reject items that require sanctioning authority review.

  * Apply special-case routing decisions, including Director self-sanction when applicable.

  * Add remarks and final decision notes.

  * Access the sanctioning inbox for delegated approval items.

### 5. Role Name: OA/DC

* **Description:** Operational verifier for resumption of duty after leave.

* **Permissions:**

  * Read routed resumption requests.

  * Verify resumption details and close the leave when valid.

  * Return a resumption item to the employee for information or correction when needed.

  * Access the resumption queue and related status history.

### 6. Role Name: Accountant / Finance

* **Description:** Finance user responsible for disbursement and reconciliation after claim approval.

* **Permissions:**

  * Read approved LTC and CPDA claims requiring financial processing.

  * Process disbursement through payroll/finance integration.

  * Reconcile financial records and update settlement status.

  * Maintain audit trail entries for financial processing actions.

  * View claim history and settlement summaries for accounting purposes.
