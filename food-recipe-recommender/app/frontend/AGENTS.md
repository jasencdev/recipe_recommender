# Repository Guidelines

## Project Structure & Module Organization
- `src/js/components/`: Reusable UI building blocks (buttons, inputs, dialogs, layout, navigation). Prefer composition; colocate component-specific styles.
- `src/js/pages/`: Route-level views (search, recommendations, recipe-detail, saved-recipes, collections, meal-planning, shopping-list, auth). Keep data-fetching at the page level.
- `src/js/services/`: API and data helpers (central axios instance, search helpers, saved-recipe cache, notes, recently viewed).
- `src/styles/` and `src/assets/`: Global styles (Tailwind) and static assets (SVG, images).
- `public/`, `index.html`, `vite.config.ts`: Static files, app shell, and Vite config (proxy to Flask backend).

Example layout:
```
src/
├─ js/
│  ├─ components/
│  ├─ pages/
│  └─ services/
├─ styles/
├─ assets/
└─ vite-env.d.ts
```

## Build, Test, and Development Commands
- `npm run dev`: Start Vite dev server with HMR. Proxies `/api` to `http://127.0.0.1:5000`.
- `npm run build`: Type-check (`tsc -b`) and build production assets with Vite.
- `npm run preview`: Serve the production build locally to validate artifacts.
- `npm run lint`: Run ESLint for TypeScript/React (hooks + refresh plugins).

Notes:
- Run the Flask backend locally for authenticated flows and real API responses.
- Node 18+ recommended. Use `npm ci` in CI to ensure lockfile fidelity.

## Architecture Overview
- Framework: React 19 + TypeScript, built with Vite 7.
- Styling: Tailwind CSS 4; components are headless-first, styled via utilities.
- Routing: React Router DOM 7; route components live in `src/js/pages/`.
- Auth: Session cookies; `AuthContext` provides user state; `ProtectedRouter` gates private routes.
- API: Central `axios` client in `src/js/services/api.ts` with `baseURL: '/api'` and `withCredentials: true`.

## Coding Style & Naming Conventions
- Indentation: 2 spaces. Use semicolons; prefer single quotes; include trailing commas where allowed.
- Files: Prefer kebab-case for pages/components (e.g., `saved-recipes.tsx`). Follow adjacent patterns where mixed (e.g., `ProtectedRouter.tsx`).
- Components: PascalCase in code; one component per file when possible.
- Imports: Use relative imports; avoid deep cross-layer imports (pages → services/components only).
- ESLint: JS/TS recommended rules + React Hooks latest + React Refresh. Fix warnings before PR approval.
- Types: Favor explicit interfaces for API data; keep domain types in `services/`.

## Testing Guidelines
- No test runner is configured. If adding tests, use Vitest + React Testing Library.
- Placement: co-locate as `*.test.ts(x)` next to source or under `src/__tests__/`.
- Mocking: Stub axios calls to `/api` and simulate auth states via context.
- Coverage: Target critical flows (auth gating, search filters, saved-recipe toggles) and pure utils. Aim ≥80% for new modules.

## Commit & Pull Request Guidelines
- Commits: Imperative mood, concise subject (≤50 chars), descriptive body when needed.
  - Examples: `feat(search): add cuisine filter`, `fix(auth): refresh user on login`, `refactor(ui): extract stacked layout`.
- Branches: `type/short-topic` (e.g., `feat/meal-planning-dnd`).
- PRs must include: summary, screenshots/GIFs for UI, reproduction steps, linked issues, and notable trade-offs.
- Required checks: `npm run lint` and `npm run build` pass locally; no unused exports; types are clean.

## Security & Configuration Tips
- Dev proxy: Vite forwards `/api` to Flask (`vite.config.ts`). Keep backend CORS aligned with `withCredentials: true`.
- Env vars: Use `VITE_` prefix for frontend consumption (e.g., `VITE_API_BASE`). Store machine-specific secrets in `.env.local` (gitignored).
- Cookies: Backend should set `HttpOnly`, `Secure` (in prod), and compatible `SameSite`. Frontend relies on browser-managed cookies.
- Data hygiene: Validate and sanitize API responses in services; never trust client input.

## Local Development Workflow
1) Install dependencies: `npm install`.
2) Start Flask backend (default `http://127.0.0.1:5000`).
3) Run frontend: `npm run dev` and open the served URL.
4) Commit small, focused changes; include screenshots for UI.
5) Before PR: `npm run lint && npm run build && npm run preview`.

## Troubleshooting
- CORS or 401 on requests: Ensure backend is running and Vite proxy is active; verify cookies are set and `withCredentials` enabled.
- Infinite redirects on protected pages: Check `AuthContext` initialization and `ProtectedRouter` guard.
- Types failing on build: Run `npm run lint` to catch rule violations; verify TS versions match lockfile.
- Assets not loading: Place static files in `public/` or import from `src/assets/`.

## Contribution Scope
- Keep pages thin; push reusable UI into `components/` and data logic into `services/`.
- Prefer incremental UI improvements over broad rewrites; align with existing patterns and Tailwind utility conventions.

Thank you for contributing to the recipe recommender frontend! This guide aims to make changes predictable, testable, and easy to review. If anything is unclear, propose improvements via PR.
