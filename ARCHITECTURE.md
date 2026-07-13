# Architecture Overview

This document serves as a critical, living template designed to equip agents
with a rapid and comprehensive understanding of the codebase's architecture,
enabling efficient navigation and effective contribution from day one. Update
this document as the codebase evolves.

## 1. Project Structure

This section provides a high-level overview of the project's directory and file
structure, categorised by architectural layer or major functional area. It is
essential for quickly navigating the codebase, locating relevant files, and
understanding the overall organization and separation of concerns.

```bash
[Project Root]/
├── backend/              # Contains all server-side code and APIs
│   ├── src/              # Main source code for backend services
│   │   ├── api/          # API endpoints and controllers
│   │   ├── client/       # Business logic and service implementations
│   │   ├── models/       # Database models/schemas
│   │   └── utils/        # Backend utility functions
│   ├── config/           # Backend configuration files
│   ├── tests/            # Backend unit and integration tests
├── frontend/             # Contains all client-side code for user interfaces
│   ├── src/              # Main source code for frontend applications
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Application pages/views
│   │   ├── assets/       # Images, fonts, and other static assets
│   │   ├── services/     # Frontend services for API interaction
│   │   └── store/        # State management (e.g., Redux, Vuex, Context API)
│   ├── public/           # Publicly accessible assets (e.g., index.html)
│   ├── tests/            # Frontend unit and E2E tests
│   └── package.json      # Frontend dependencies and scripts
├── common/               # Shared code, types, and utilities used by both frontend and backend
│   ├── types/            # Shared TypeScript/interface definitions
│   └── utils/            # General utility functions
├── docs/                 # Project documentation (e.g., API docs, setup guides)
├── scripts/              # Automation scripts (e.g., deployment, data seeding)
├── .github/              # GitHub Actions or other CI/CD configurations
├── .gitignore            # Specifies intentionally untracked files to ignore
├── README.md             # Project overview and quick start guide
├── GLOSSARY.md           # Domain-specific terms and their definitions
└── ARCHITECTURE.md       # This document
```

## 2. High-Level System Diagram

A simple block diagram of the major components and their interactions. Shows how
data flows, how services communicate, and key architectural boundaries.

Frontend Flow

```
[User] → [React Native (Expo)] → [React Query (server state) + WatermelonDB (local state)] → [Supabase Real-time (sync)]
```

Backend Flow

```
[Supabase Auth] → [PostgreSQL (with RLS policies)] ← [Optional future: Node/Deno edge function (for AI calls via OpenAI API)]
```

## 3. Core Components

(List and briefly describe the main components of the system. For each, include
its primary responsibility and key technologies used.)

### 3.1. Frontend

Name: Mobile App

Description: The main user interface for interacting with the system, allowing
users to manage their profiles, view and edit their data, and initiate
workflows.

Technologies: React Native with Expo

Deployment: [Expo](https://expo.dev/)

UI Component Library: React Native Paper

Offline-first: Tanstack Query + expo-sqlite

## 4. Data Stores

(List and describe the databases and other psersistent storage solutions used.)

### 4.1. Supabase

Name: Primary User Database, Analytics Data Warehouse, Auth

Type: PostgreSQL

Purpose: Privately store user data

Key Schemas: households, users, pantry_items, shopping_lists, list_items,
meal_plans, meals, invitations

## 5. External Integrations / APIs

Name: Supabase Realtime

Purpose: Real-time Sync

Description:

1. Store data locally in SQLite

   Queries happen against local SQLite first (instant, offline) You maintain the
   schema locally

2. Use @tanstack/react-query to manage Supabase API calls

   Mutations write to Supabase Queries fetch from Supabase and update local
   SQLite useQuery options: staleTime, cacheTime, background refetching

3. Sync strategy

   When offline: read from SQLite, queue mutations in AsyncStorage When online:
   flush mutation queue to Supabase, fetch latest data Use Supabase Realtime
   subscriptions to stay in sync

See examples:

- [Offline storage](examples/frontend/offline.js)
- [Sync after entwork is restored](examples/frontend/sync.js)

## 6. Deployment & Infrastructure

Cloud Providers: Vercel or App Store/Play Store

CI/CD Pipeline: Github Actions + EAS (Expo Application Services)

## 7. Security Considerations

Authentication: User authentication via Supabase (magic link, biometric,
passphrase). Row-level security: users can only query rows where
user_id=auth.uid()

Authorizations: Shopping list, meal plans, and pantry items are all tied to
household_id. RLS policies protect each table.

Data Encryption: Supabase encrypts data at rest in the hosted PostgreSQL. HTTPS
encrypts the data in transit. Expo-sqlite encrypts local SQLite via SQLCyper;
keys never leave device

Key Security Tools/Practices: regular security audits

## 8. Development & Testing Environment

Local Setup Instructions: [CONTRIBUTING.MD](CONTRIBUTING.md)

Testing Frameworks:

- Unit: Jest + React Native Testing Library
- Integration: Expo Router
- E2E: EAS Workflows with Maestro

Code Quality Tools:

- Prettier
- ESlint
- Github Code scanning alerts
- Depandabot

## 9. Future Considerations / Roadmap

## 10. Project Identification

Project Name: Kitchen Manger

Repository URL:
[https://github.com/AquaticAlpaca/kitchen-manager/](https://github.com/AquaticAlpaca/kitchen-manager/)

Primary Contact/Team:
[https://github.com/AquaticAlpaca/](https://github.com/AquaticAlpaca/)

Date of Last Update: 2026-07-13
