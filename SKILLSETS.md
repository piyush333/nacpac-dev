# NacPac Dev Agent Skillsets

## Overview
NacPac Dev Agent possesses 7 core technical skillsets to handle code development, building mobile/desktop apps, and deployments. Each skillset is versioned and documented for continuous improvement.

---

## 1. **nacpac_codebase**

**Version:** 1.0

**Description:**
Deep knowledge of the NacPac custom sticker printing application architecture, including mobile and desktop codebases, build processes, and deployment workflows.

**Key Technologies:**
- React Native (mobile app)
- Express.js (backend API)
- PostgreSQL (database)
- Node.js ecosystem
- Electron (potential desktop wrapper)

**Key Files:**
- `/mobile/app/index.tsx` — React Native entry point
- `/desktop/main.js` — Electron main process
- `/backend/server.js` — Express API server
- `/package.json` — Dependencies & build scripts
- `/mobile/eas.json` — Expo build config

**Capabilities:**
- Navigate NacPac's codebase structure
- Understand app architecture and component hierarchy
- Modify features (stickers, printing, user accounts)
- Debug integration issues between mobile/desktop/backend
- Generate context about current build state

**Known Issues & Workarounds:**
- EAS build requires manual approval via Discord
- Windows EXE packaging may require additional Windows SDK setup
- APK backups go to Cloudflare R2 + Google Drive

---

## 2. **python**

**Version:** 1.0

**Description:**
Python scripting and automation for agent tooling, data processing, and system integration.

**Technology:** Python 3.9+

**Use Cases:**
- Build orchestration scripts
- Backup management (backup_to_gdrive.py, build_backup.py)
- Task routing and processing
- Database migrations and queries
- Discord bot scripting

**Key Libraries:**
- `supabase-py` — Database client
- `discord.py` — Discord bot framework
- `subprocess` — Shell command execution
- `logging` — System logging
- `requests` — HTTP client

**Capabilities:**
- Write and execute build scripts
- Manage Supabase queries and updates
- Parse and transform JSON/CSV data
- Orchestrate multi-step workflows
- Error handling and retry logic

---

## 3. **nodejs**

**Version:** 1.0

**Description:**
Node.js runtime and ecosystem for backend development, build tools, and tooling.

**Technology:** Node.js 18+

**Use Cases:**
- Express.js server development
- npm package management
- Build script execution (EAS, webpack)
- API integration and middleware
- Server-side authentication

**Key Frameworks:**
- Express.js — Web framework
- EAS CLI — Expo build service
- npm — Package manager
- webpack — Module bundler

**Capabilities:**
- Build Express APIs
- Manage npm dependencies
- Run build tools (EAS, webpack)
- Execute Node.js scripts
- Debug server issues

**Dependencies Management:**
- package.json format
- npm install/update/prune
- Dependency conflict resolution

---

## 4. **react**

**Version:** 1.0

**Description:**
React and React Native component development, state management, and UI architecture.

**Technology Stack:**
- React 18+
- React Native (mobile)
- React Hooks (state management)
- TypeScript (type safety)
- CSS/Flexbox (styling)

**Use Cases:**
- Mobile UI component development (React Native)
- Web UI development (potential future)
- State management with useState/useContext
- Side effects with useEffect
- Custom hooks creation

**Key Libraries:**
- `react-native` — Mobile framework
- `@react-navigation` — Navigation
- `expo` — Development platform
- `typescript` — Type checking

**Capabilities:**
- Build responsive mobile interfaces
- Manage component state and lifecycle
- Create reusable UI components
- Handle user input and navigation
- Optimize performance with memoization

**Component Patterns:**
- Functional components with hooks
- Props drilling and context API
- Custom hooks for logic reuse
- Error boundaries

---

## 5. **expo_dev**

**Version:** 1.0

**Description:**
Expo development platform for React Native app building, testing, and APK generation via EAS.

**Technology:** Expo SDK 48+, EAS Build Service

**Use Cases:**
- Local development with Expo Go
- APK building via EAS
- Device testing (iOS/Android)
- Over-the-air updates
- Build profile management

**Key Configuration Files:**
- `app.json` — Expo app config
- `eas.json` — EAS build profiles
- `expo.json` — Expo settings

**EAS Build Profiles:**
- `production` — Optimized APK for app stores
- `preview` — Beta testing APK
- `development` — Dev APK for testing

**Capabilities:**
- Run Expo dev server locally
- Build APK via EAS (with manual approval)
- Manage build profiles and signing
- Test on physical devices
- View build logs and debug issues

**Workflow:**
1. Configure `eas.json` build profile
2. Run `eas build --platform android` (requires approval)
3. Monitor build progress via EAS dashboard
4. Download APK when ready
5. Backup to R2 + Google Drive

**Known Constraints:**
- EAS builds require Google Play Services certificates
- Manual Discord approval required before build
- APK signing managed by EAS service

---

## 6. **npm**

**Version:** 1.0

**Description:**
Node Package Manager for dependency management, build script execution, and package distribution.

**Technology:** npm 9+

**Use Cases:**
- Install/update project dependencies
- Execute build scripts defined in package.json
- Manage dev vs. production dependencies
- Create custom npm scripts
- Version management and updates

**Key Commands:**
- `npm install` — Install dependencies
- `npm run <script>` — Execute build scripts
- `npm update` — Update packages
- `npm prune` — Remove unused dependencies
- `npm audit` — Check for vulnerabilities

**Build Scripts Managed:**
- `npm run build` — Compile/bundle app
- `npm run dev` — Start dev server
- `npm run test` — Run tests
- Custom deployment scripts

**Capabilities:**
- Manage project dependencies
- Execute build pipelines
- Handle version conflicts
- Optimize bundle sizes
- Integrate with CI/CD

**Package Management:**
- Semantic versioning (semver)
- Lock file management (package-lock.json)
- Peer dependency resolution

---

## 7. **exe_windows**

**Version:** 1.0

**Description:**
Windows executable packaging and distribution for NacPac Desktop app (Electron or npm build tools).

**Technology:** Electron or webpack-based bundler, Windows Installer tools

**Use Cases:**
- Package web app as standalone EXE
- Windows installer creation (.msi, .exe)
- Desktop app distribution
- Auto-update mechanisms
- Windows certificate signing

**Build Tools:**
- Electron (desktop framework)
- electron-builder (packaging)
- NSIS (installer generation)
- Code signing tools

**Build Output:**
- `NacPac-Setup.exe` — Windows installer
- `NacPac.exe` — Portable executable
- `.msi` — MSI installer package

**Capabilities:**
- Bundle web app for Windows
- Create installation packages
- Configure auto-updates
- Handle Windows registry integration
- Code signing for distribution

**Build Pipeline:**
1. Prepare bundled app (npm build)
2. Configure electron-builder
3. Generate installers (.exe, .msi)
4. Sign executables (optional)
5. Upload to storage (R2, Google Drive)

**Known Constraints:**
- Windows SDK may be required locally
- Code signing requires certificates
- EXE generation takes 5-10 minutes

**Distribution:**
- Upload to Cloudflare R2
- Backup to Google Drive
- Create GitHub releases with EXE

---

## Usage in Agent Context

When NacPac Dev Agent initializes, it loads these 7 skillsets from the Supabase `agent_skillsets` table and formats them as context to inject into Claude's system prompt:

```
You are NacPac Dev Agent with these skillsets:
• NACPAC_CODEBASE - Deep knowledge of NacPac app architecture...
• PYTHON - Python 3.9+ scripting and automation...
• NODEJS - Node.js 18+ backend and tooling...
• REACT - React and React Native development...
• EXPO_DEV - Expo platform for React Native builds...
• NPM - npm dependency and build management...
• EXE_WINDOWS - Windows executable packaging...
```

This context is prepended to every task execution, ensuring the agent has access to technical knowledge when solving problems.

---

## Versioning & Updates

- **Current Version:** 1.0 (2026-07-17)
- **Next Update:** Phase 2 — Add machine learning optimization skillset
- **Maintenance:** Review quarterly for new tools/frameworks

## Related Files

- `agentic/agents/nacpac_dev.py` — Agent implementation
- `agentic/memory.py` — Skillset loading from Supabase
- `migrations/001_create_agent_skillsets.sql` — Database schema
- `AGENT_NACPAC_DEV_SESSION.md` — Session handoff document
