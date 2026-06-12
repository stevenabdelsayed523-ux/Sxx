# CodeMate AI

> Your AI pair-programmer that never sleeps.

CodeMate AI is an intelligent coding assistant that writes, debugs, and refactors code in real-time. It understands your full codebase and works across any language or framework.

## Project Structure

```
Sxx/
├── frontend/          # Vite + React + TypeScript web app
│   ├── src/           # React components and styles
│   ├── index.html     # Entry HTML
│   ├── vite.config.ts # Vite config with API proxy
│   └── package.json
├── backend/           # Node.js + Express + TypeScript API
│   ├── src/           # Server source code
│   │   ├── index.ts   # Express server entry point
│   │   └── app.test.ts
│   ├── tsconfig.json
│   └── package.json
├── .github/
│   └── workflows/
│       └── ci.yml     # GitHub Actions CI pipeline
├── Dockerfile         # Backend container build
├── .eslintrc.json     # Shared ESLint configuration
├── .prettierrc        # Shared Prettier configuration
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Backend

```bash
cd backend
npm install
npm run dev     # starts dev server on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev     # starts dev server on http://localhost:3000 (proxies /api to backend)
```

### Production Build

```bash
cd frontend && npm run build   # produces dist/ folder
cd backend  && npm run build   # compiles TypeScript to dist/
```

### Docker

```bash
docker build -t codemate-ai-backend .
docker run -p 8000:8000 codemate-ai-backend
```

## Tech Stack

- **Frontend:** React 18, TypeScript, Vite
- **Backend:** Node.js, Express, TypeScript
- **CI:** GitHub Actions (lint, type-check, test)

## License

MIT