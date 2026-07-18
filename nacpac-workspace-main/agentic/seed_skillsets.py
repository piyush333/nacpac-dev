"""Seed NacPac Dev Agent skillsets into Supabase."""

import logging
from agentic.memory import memory

logger = logging.getLogger(__name__)


NACPAC_DEV_SKILLSETS = [
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "nacpac_codebase",
        "description": "Deep knowledge of NacPac custom sticker printing app architecture (React Native mobile, Express.js backend, PostgreSQL database)",
        "documentation": """NacPac Codebase Skillset

Key Technologies:
- React Native (mobile app)
- Express.js (backend API)
- PostgreSQL (database)
- Node.js ecosystem

Key Files:
- /mobile/app/index.tsx - React Native entry point
- /desktop/main.js - Electron main process
- /backend/server.js - Express API server
- /package.json - Dependencies & build scripts
- /mobile/eas.json - Expo build config

Capabilities:
- Navigate NacPac's codebase structure
- Understand app architecture and component hierarchy
- Modify features (stickers, printing, user accounts)
- Debug integration issues between mobile/desktop/backend
- Generate context about current build state

Known Issues:
- EAS build requires manual approval via Discord
- Windows EXE packaging may require Windows SDK setup
- APK backups go to Cloudflare R2 + Google Drive""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "python",
        "description": "Python 3.9+ scripting, automation, and tooling for build orchestration and system integration",
        "documentation": """Python Skillset (3.9+)

Use Cases:
- Build orchestration scripts
- Backup management (backup_to_gdrive.py, build_backup.py)
- Task routing and processing
- Database migrations and queries
- Discord bot scripting

Key Libraries:
- supabase-py - Database client
- discord.py - Discord bot framework
- subprocess - Shell command execution
- logging - System logging
- requests - HTTP client

Capabilities:
- Write and execute build scripts
- Manage Supabase queries and updates
- Parse and transform JSON/CSV data
- Orchestrate multi-step workflows
- Error handling and retry logic""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "nodejs",
        "description": "Node.js 18+ runtime and ecosystem for backend development, build tools, and server integration",
        "documentation": """Node.js Skillset (18+)

Use Cases:
- Express.js server development
- npm package management
- Build script execution (EAS, webpack)
- API integration and middleware
- Server-side authentication

Key Frameworks:
- Express.js - Web framework
- EAS CLI - Expo build service
- npm - Package manager
- webpack - Module bundler

Capabilities:
- Build Express APIs
- Manage npm dependencies
- Run build tools (EAS, webpack)
- Execute Node.js scripts
- Debug server issues

Dependencies Management:
- package.json format
- npm install/update/prune
- Dependency conflict resolution""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "react",
        "description": "React and React Native component development, state management, hooks, and UI architecture",
        "documentation": """React Skillset

Technology Stack:
- React 18+
- React Native (mobile)
- React Hooks (state management)
- TypeScript (type safety)
- CSS/Flexbox (styling)

Use Cases:
- Mobile UI component development (React Native)
- Web UI development (potential future)
- State management with useState/useContext
- Side effects with useEffect
- Custom hooks creation

Key Libraries:
- react-native - Mobile framework
- @react-navigation - Navigation
- expo - Development platform
- typescript - Type checking

Capabilities:
- Build responsive mobile interfaces
- Manage component state and lifecycle
- Create reusable UI components
- Handle user input and navigation
- Optimize performance with memoization

Component Patterns:
- Functional components with hooks
- Props drilling and context API
- Custom hooks for logic reuse
- Error boundaries""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "expo_dev",
        "description": "Expo development platform for React Native: local dev, APK building via EAS, device testing, and OTA updates",
        "documentation": """Expo Development Skillset

Technology: Expo SDK 48+, EAS Build Service

Use Cases:
- Local development with Expo Go
- APK building via EAS
- Device testing (iOS/Android)
- Over-the-air updates
- Build profile management

Key Configuration Files:
- app.json - Expo app config
- eas.json - EAS build profiles
- expo.json - Expo settings

EAS Build Profiles:
- production - Optimized APK for app stores
- preview - Beta testing APK
- development - Dev APK for testing

Capabilities:
- Run Expo dev server locally
- Build APK via EAS (requires manual approval)
- Manage build profiles and signing
- Test on physical devices
- View build logs and debug issues

Workflow:
1. Configure eas.json build profile
2. Run 'eas build --platform android' (requires Discord approval)
3. Monitor build progress via EAS dashboard
4. Download APK when ready
5. Backup to R2 + Google Drive

Constraints:
- EAS builds require Google Play Services certificates
- Manual Discord approval required before build
- APK signing managed by EAS service""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "npm",
        "description": "Node Package Manager for dependency management, build script execution, and package distribution",
        "documentation": """npm Skillset

Technology: npm 9+

Use Cases:
- Install/update project dependencies
- Execute build scripts defined in package.json
- Manage dev vs. production dependencies
- Create custom npm scripts
- Version management and updates

Key Commands:
- npm install - Install dependencies
- npm run <script> - Execute build scripts
- npm update - Update packages
- npm prune - Remove unused dependencies
- npm audit - Check for vulnerabilities

Build Scripts Managed:
- npm run build - Compile/bundle app
- npm run dev - Start dev server
- npm run test - Run tests
- Custom deployment scripts

Capabilities:
- Manage project dependencies
- Execute build pipelines
- Handle version conflicts
- Optimize bundle sizes
- Integrate with CI/CD

Package Management:
- Semantic versioning (semver)
- Lock file management (package-lock.json)
- Peer dependency resolution""",
        "version": "1.0"
    },
    {
        "agent_id": "nacpac_dev",
        "skillset_name": "exe_windows",
        "description": "Windows executable packaging: Electron bundling, installer creation, and Windows distribution (.exe, .msi)",
        "documentation": """Windows EXE Skillset

Technology: Electron or webpack-based bundler, Windows Installer tools

Use Cases:
- Package web app as standalone EXE
- Windows installer creation (.msi, .exe)
- Desktop app distribution
- Auto-update mechanisms
- Windows certificate signing

Build Tools:
- Electron - Desktop framework
- electron-builder - Packaging
- NSIS - Installer generation
- Code signing tools

Build Output:
- NacPac-Setup.exe - Windows installer
- NacPac.exe - Portable executable
- .msi - MSI installer package

Capabilities:
- Bundle web app for Windows
- Create installation packages
- Configure auto-updates
- Handle Windows registry integration
- Code signing for distribution

Build Pipeline:
1. Prepare bundled app (npm build)
2. Configure electron-builder
3. Generate installers (.exe, .msi)
4. Sign executables (optional)
5. Upload to storage (R2, Google Drive)

Constraints:
- Windows SDK may be required locally
- Code signing requires certificates
- EXE generation takes 5-10 minutes

Distribution:
- Upload to Cloudflare R2
- Backup to Google Drive
- Create GitHub releases with EXE""",
        "version": "1.0"
    }
]


def seed_skillsets():
    """Insert all NacPac Dev skillsets into Supabase."""
    if not memory.client:
        logger.error("Supabase client not initialized. Cannot seed skillsets.")
        return False

    try:
        # First, check if skillsets already exist and delete them to avoid conflicts
        logger.info("Checking for existing skillsets...")
        existing = memory.client.table("agent_skillsets").select("id").eq("agent_id", "nacpac_dev").execute()

        if existing.data:
            logger.info(f"Found {len(existing.data)} existing skillsets. Deleting...")
            for row in existing.data:
                memory.client.table("agent_skillsets").delete().eq("id", row["id"]).execute()

        # Insert new skillsets
        logger.info(f"Inserting {len(NACPAC_DEV_SKILLSETS)} skillsets for nacpac_dev...")
        for skillset in NACPAC_DEV_SKILLSETS:
            result = memory.client.table("agent_skillsets").insert(skillset).execute()
            if result.data:
                logger.info(f"✅ Seeded skillset: {skillset['skillset_name']}")
            else:
                logger.error(f"❌ Failed to seed skillset: {skillset['skillset_name']}")
                return False

        logger.info("✅ All skillsets seeded successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to seed skillsets: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = seed_skillsets()
    exit(0 if success else 1)
