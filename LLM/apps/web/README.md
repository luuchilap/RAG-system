# Frontend Application

Next.js 15 frontend for the Local LLM Chatbot application.

## Setup

This project uses **pnpm** for package management (not npm). Make sure you have pnpm installed:

```bash
npm install -g pnpm
```

## Installation

From the **LLM** directory (root of monorepo):

```bash
pnpm install
```

## Development

### Run from monorepo root:
```bash
cd LLM
pnpm dev
```

### Or run just the web app:
```bash
cd LLM/apps/web
pnpm dev
```

The app will be available at http://localhost:3000

## Environment Variables

Create a `.env.local` file in `apps/web/`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features

- ✅ Authentication (Login/Register)
- ✅ Protected routes
- ✅ Navigation with auth state
- ⏳ Chat interface (Task 6)
- ⏳ Document upload (Task 8)

## Project Structure

```
apps/web/
├── app/              # Next.js App Router pages
│   ├── login/        # Login page
│   ├── register/     # Registration page
│   ├── chat/         # Chat page (protected)
│   └── documents/    # Documents page (protected)
├── components/        # React components
│   ├── navigation.tsx
│   └── protected-route.tsx
├── hooks/            # React hooks
│   └── useAuth.tsx   # Authentication hook
└── lib/              # Utilities
    └── api.ts        # API client functions
```

## Troubleshooting

### "next: command not found"
- Make sure you're using `pnpm` not `npm`
- Run `pnpm install` from the LLM directory first

### "Unsupported URL Type workspace:"
- This is a pnpm workspace, you must use `pnpm` not `npm`
- Install pnpm: `npm install -g pnpm`

### Port 3000 already in use
- Change port: `pnpm dev -- -p 3001`
- Or kill the process using port 3000

