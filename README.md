[README.md](https://github.com/user-attachments/files/27757623/README.md)[Uploading README.# MIT Connect Frontend

This folder contains the Vite React frontend for MIT Connect. It provides the role-based UI for Student, Admin, Faculty, and Finance users.

## Key Features

- Multi-role login interface and dashboards
- Role-specific sidebar menus and pages
- Responsive layout for desktop and mobile screens
- Local demo authentication using localStorage
- Real-time UI updates for invoices and fee assignments using CustomEvent

## Setup (Local)

### Prerequisites

- Node.js 18+

### Install and Start

```bash
npm install
npm run dev
```

Open the local Vite URL printed in the terminal.

### Production Build

```bash
npm run build
```

## UI Flow Architecture

### High-Level

```
[Login] -> [Role Dashboard] -> [Role Pages]
```

### Invoice and Fee Pipeline (UI)

1. Admin assigns fees to approved students.
2. Admin generates invoice for a fee assignment.
3. Student pays the fee (90 percent success simulation in UI).
4. Fee assignment status updates to paid.
5. Matching invoice updates to Paid.
6. Admin dashboard updates in real-time via custom events.

### Event Sync

- feeAssignmentUpdated keeps student fee list synchronized.
- invoiceUpdated refreshes invoice lists and dashboard stats.

For full pipeline details, see [../INVOICE_PIPELINE_IMPLEMENTATION.md](../INVOICE_PIPELINE_IMPLEMENTATION.md).

## Technologies Used

- React
- Vite
- React Router
- CSS3
- JavaScript (ES Modules)
md…]()
