# Frontend Project Structure & Development Guide

## 📁 Project Structure

```
frontend/
│
├── assets/            # Images, icons, SVGs
│
├── components/        # Reusable UI components (Initial)
│   ├── button.js
│   ├── input.js
│   ├── card.js
│   └── navbar.js
│
├── pages/             # Feature-based pages (by user story)
│   ├── home/
│   │   ├── home.html
│   │   ├── home.js
│   │   └── home.css
│   │
│   ├── auth/
│   │   ├── auth.html
│   │   ├── auth.js
│   │   └── auth.css
│
├── services/          # API calls & business logic
│   ├── apiClient.js   # Base fetch handler (token, headers, errors)
│   ├── authService.js # Login, register, token management
│   └── userService.js # User-related API calls
│
├── middleware/        # Frontend "middleware" logic
│   ├── authGuard.js   # Protect routes/pages
│   └── interceptor.js # (Optional) global handlers
│
├── store/             # Simple state management
│   └── authStore.js   # Token storage
│
├── utils/             # Helper functions
│   ├── fetch.js       # Wrapper around fetch for common patterns
│   └── validate.js    # Form validation helpers
│
├── styles/            # Global styles (Tailwind, base CSS)
│   └── main.css
│
├── config/            # Global constants/config
│   └── constants.js
│
└── main.js            # Entry point
```

---

## 🧠 Architecture Overview

This project follows a **layered structure**:

- **Pages** → UI + interaction logic
- **Components** → reusable UI building blocks
- **Services** → API communication
- **Middleware** → cross-cutting logic (auth, redirects)
- **Store** → state (e.g., authentication token)

---

## 🔁 Data Flow

```
Page → Service → apiClient → Backend (Flask)
```

- Pages NEVER call `fetch()` directly
- All API calls go through `apiClient.js`

---

## 📦 Responsibilities

### 1. Components (`/components`)

- Reusable UI elements (Button, Input, Card, etc.)
- Must follow shared styling rules (color, spacing, radius)
- No API calls or business logic

---

### 2. Pages (`/pages`)

- Organized by **feature (user story)**
- Each page contains:
  - HTML (structure)
  - JS (logic)
  - CSS (only if needed)

---

### 3. Services (`/services`)

- Handle API communication
- Use `apiClient.js` internally
- Example:
  - `authService.js` → login, register
  - `userService.js` → user data

---

### 4. apiClient (`apiClient.js`)

- Centralized API handler
- Responsibilities:
  - Attach auth token
  - Set headers
  - Handle errors (e.g., 401)

---

### 5. Middleware (`/middleware`)

- Cross-page logic
- Example:
  - `authGuard.js` → block unauthorized access

---

### 6. Store (`/store`)

- Simple state management
- Example:
  - Store auth token in `localStorage`

---

## ⚠️ Development Rules (IMPORTANT)

### ❌ DO NOT:

- Call `fetch()` directly inside pages
- Duplicate UI components (e.g., multiple button styles)
- Hardcode API URLs
- Handle auth token in multiple places
- Write random/unstructured CSS per page

---

### ✅ ALWAYS:

- Use components from `/components`
- Call APIs via `/services`
- Use `apiClient.js` for all HTTP requests
- Store token only in `/store/authStore.js`
- Protect private pages using `authGuard`
- Follow shared UI guidelines (colors, spacing, radius)

---

## 🔐 Authentication Flow

### Login:

1. User submits form
2. `authService.login()` is called
3. Token is returned from backend
4. Token is saved in `authStore`

---

### Access Protected Page:

1. Page calls `requireAuth()`
2. If no token → redirect to login page

---

### API Request:

1. Page calls service
2. `apiClient` attaches token automatically
3. Backend validates token

---

## 🧩 Adding New Features (User Story Workflow)

1. Create a new folder in `/pages`
2. Build UI using shared components
3. Add logic in `.js`
4. Call APIs via `/services`
5. If needed:
   - Create new component → `/components`
   - Add new service → `/services`

---

## 🎯 Goal of This Structure

- Maintain **UI consistency**
- Avoid duplicated logic
- Enable **parallel development**
- Keep code **scalable and maintainable**

---

## 💡 Notes

- Keep code modular and reusable
- Always think in **components + features**, not files
- This structure is designed to grow with the project while keeping it organized and maintainable.
