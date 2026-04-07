# Forge Master Changelog

This is the canonical running record of what has been changed in Forge.

Purpose:
- give any human or agent a single place to understand what Forge is now
- track shipped work, product decisions, infra changes, and live environment details
- reduce lost context between chats, sessions, and contributors

Update rule:
- update this file after every completed implementation, bug fix, deploy, or meaningful product change
- if a change affects live behavior, note both the code change and the runtime/deploy impact

## Canonical Project Identity

- Product name: `Forge`
- Local workspace: `/Users/carsonweso/Documents/Forge 2.0`
- GitHub repo: `https://github.com/carswqqqq1/forge-2.0`
- Primary live frontend: `https://forge-2-0-fsvibxs.netlify.app`

## Product Direction

Forge is being built as:
- an agentic SaaS app
- inspired by Manus
- upgraded with missing Manus features and stronger execution UX
- expanded with Claude Code style coding and workspace behavior
- designed in a premium black-and-white visual style

Core product goals:
- feel like Manus
- be more transparent than Manus
- support research, execution, code, files, browser work, and outputs in one place
- become sellable as a hosted SaaS

## Major Product Changes Completed

### 1. Repo And Workspace Setup

- Imported the `ai-manus` codebase into Forge’s repo/workspace as the technical baseline
- Standardized the project around:
  - local folder: `/Users/carsonweso/Documents/Forge 2.0`
  - repo: `forge-2.0`
- Added local run helpers and deployment config

### 2. Branding Shift From Manus To Forge

- Visible app branding changed from `Manus` / `Forge 2.0` to `Forge`
- Removed visible Claw branding and disabled Claw-facing UI/runtime paths
- Removed GitHub repo button from the runtime shell
- Shifted visible text, headings, app title, and logos toward Forge branding

Important note:
- some deep internal legacy names may still exist in code/package history because the project started from Manus code

### 3. Local Runtime Setup

- Configured Forge to run locally with:
  - frontend on `http://localhost:5173`
  - backend on `http://localhost:8000`
  - MongoDB
  - Redis
  - sandbox container
  - mockserver
- Added/startup helpers including `start-forge.sh`
- Wired local env toward NVIDIA-hosted model usage by default

### 4. NVIDIA Model Setup

- Added support for NVIDIA API Catalog / NIM style OpenAI-compatible calls
- Added example scripts and env templates for NVIDIA-backed chat
- Wired backend defaults to NVIDIA-compatible config

Current mode structure:
- `Forge Lite`
- `Forge`
- `Forge Max`

Current model routing baseline:
- lite: low-cost / lightweight mode
- regular: balanced mode
- max: strongest available mode

The exact mapped model names have been adjusted over time as the app evolved and may continue to change.

### 5. Credit System

- Added persistent user credit balance
- Added per-session credit charging
- Added model-aware cost estimation
- Added budget caps and budget/risk/access metadata to sessions
- Added UI credit display
- Added zero-credit lockout behavior
- Users can no longer start new work when credits are depleted

Default balance behavior was later adjusted manually for the current working user during testing.

### 6. Persistent Memory

- Added cross-chat memory brief generation
- New sessions can inherit summarized recent context
- Added hooks for future memory model separation
- Persistent memory currently uses a recent-session summary approach rather than a full embeddings retrieval system

### 7. Session / Sandbox / Browser Isolation

- Each chat is intended to have its own sandbox computer
- Stop/delete paths destroy associated sandboxes
- Added stricter browser reset behavior for fresh chats:
  - closes stale tabs
  - clears cookies
  - clears browser cache
  - performs best-effort local/session storage cleanup
  - resets to a blank page
- Added safer sandbox recovery if a stored sandbox cannot be restored
- Stopped sessions now clear dead sandbox/task references so a resumed session does not attach to broken state

Why this matters:
- fixes the “restore pages” problem
- reduces browser-state leakage between chats
- makes each new chat feel like a fresh computer

### 8. English-Only UX Pass

- Forced visible UI into English-only behavior
- Removed visible Chinese-facing options from the main runtime experience
- Cleaned multiple Forge-facing prompts and labels

### 9. Error Handling / Stability Fixes

- Fixed session creation failures caused by missing backend env/config
- Fixed model/session startup issues
- Fixed missing user credit values in auth responses
- Fixed malformed tool-name handling
- Added compatibility aliasing for browser search tool calls
- Reduced raw/ugly browser and tool errors leaking into the UI
- Soft-failed bad browser pages like 404s instead of crashing the entire task
- Fixed notification/tool-message handling so user-facing messages are treated correctly

### 10. Home / Sidebar / Chat UI Overhaul

- Reworked the app shell to closely match Manus
- Rebuilt the sidebar structure with:
  - lowercase Forge logo
  - new task button
  - agents/search/library nav
  - projects section
  - task list controls
  - bottom referral panel
  - bottom utility icons
- Reworked the home page to include:
  - Manus-style editorial heading
  - centered input
  - connect-tools bar
  - quick action pills
  - onboarding cards
- Reworked chat view to include:
  - richer plan steps
  - collapsible execution flow
  - completion state UI
  - follow-up suggestions
  - model badge
  - share/export/collaborate controls

### 11. Model Selection UX

- Replaced simple mode pills with a Manus-style dropdown structure
- Added tier selection UX:
  - Forge Max
  - Forge
  - Forge Lite
- Stored model selection in frontend state/local storage

### 12. Search Modal

- Added a modal-based task search flow
- Added grouped results and keyboard shortcut support
- Search now behaves more like a global overlay than a full page switch

### 13. New App Pages

Added dedicated pages/routes for:
- `/agents`
- `/library`
- `/integrations`

What they do:
- `Agents`: sales/marketing/support style agent landing surface
- `Library`: grouped file browser by task/session
- `Integrations`: integrations/app marketplace placeholder

### 14. Connectors / Integrations UX

- Added branded connector icon row
- Added connection modal flow for integrations
- GitHub modal supports token-style entry behavior for now
- Other integrations currently use connect/coming-soon patterns

Included visual connector support for:
- Notion
- Gmail
- Google Calendar
- GitHub
- Slack
- data/browser style integrations

### 15. Wide Research Mode

- Added `wide_research` task mode
- Wide research mode can:
  - expand a topic into subtopics
  - search across multiple areas
  - synthesize a structured report
  - aim for citations / comprehensive output

### 16. Task Completion UX

- Added completed-task pill/banner
- Added star-rating row
- Added generated suggested follow-ups
- Added better plan-step completion presentation

### 17. Sharing / Session Actions

- Added session rename support
- Added share/delete flows in sidebar task menus
- Added richer chat header controls including:
  - collaborate
  - share
  - export
  - overflow menu

### 18. Netlify Frontend Deployment

- Added `netlify.toml`
- Linked and deployed the frontend to Netlify
- Current production frontend:
  - `https://forge-2-0-fsvibxs.netlify.app`

### 19. Public Backend Tunnel For Live Testing

Because Forge’s backend depends on Docker, MongoDB, Redis, and sandbox orchestration, the public backend is currently exposed through a temporary tunnel from the local machine instead of a permanent VPS.

Current tunnel at the time of this update:
- `https://901d502925f33c.lhr.life`

Important limitation:
- this is temporary
- the live site works only while the local machine, backend, and tunnel stay up

### 20. Master Changelog And Agent Update Rule

- Added this `CHANGELOG.md` as the single source of truth for Forge changes
- Added an agent rule in `AGENTS.md` requiring future completed work to update this file
- This changelog is now the main handoff/reference document for people and agents working on Forge

### 21. Security And Stability Audit Pass

Fixed in one audit pass:
- locked down env file tracking rules in `.gitignore`
- confirmed `.env` is no longer tracked by git
- strengthened `.env.example` placeholders
- replaced weak default JWT secret behavior with secure random generation
- removed insecure wildcard CORS with credentials
- removed default local admin credentials and now require explicit env values for local auth
- added auth rate limiting for login/register attempts
- added chat message length validation and request body size limiting
- added explicit auth/share validation for shared file access
- tightened chat markdown sanitization with allowlists and safe link attributes
- improved concurrent token refresh queuing on the frontend
- added browser/tool/task timeout protections to reduce hung runs
- wrapped chat SSE event handling in a defensive `try/catch`

Operational notes:
- the exact requested host `python -m uvicorn ...` restart command failed on this machine because there is no system `python` binary
- the Docker backend was restarted instead so the patched backend is the one serving Forge

### 22. Manus-Style UI Polish Pass

- set new sessions to default to `New task`
- updated chat header fallback title to `New task`
- updated model dropdown naming to:
  - Forge Max
  - Forge Regular
  - Forge Lite
- darkened running-task step chips to better match Manus
- centered the search modal and deepened the overlay background
- changed post-task follow-ups to rounded chip-style buttons
- reduced follow-up count to 3 suggestions
- added persistent local star-rating saving per session
- aligned the home quick-action `More` dropdown to the requested Forge options

## Runtime / Environment Notes

### Local Dev

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`

### Live

- frontend: `https://forge-2-0-fsvibxs.netlify.app`
- latest known deploy during this update:
  - `https://69d45855caabb6ce068ddbb9--forge-2-0-fsvibxs.netlify.app`

### Current Hosting Reality

- frontend is on Netlify
- backend is not yet on permanent infrastructure
- backend currently depends on a live local tunnel

## Important Files Added Or Changed Over Time

This list focuses on high-impact files and systems changed during the Forge rebuild:

- `/Users/carsonweso/Documents/Forge 2.0/netlify.toml`
- `/Users/carsonweso/Documents/Forge 2.0/start-forge.sh`
- `/Users/carsonweso/Documents/Forge 2.0/.env`
- `/Users/carsonweso/Documents/Forge 2.0/.env.example`
- `/Users/carsonweso/Documents/Forge 2.0/.env.nvidia.example`
- `/Users/carsonweso/Documents/Forge 2.0/scripts/nvidia_chat_example.py`
- `/Users/carsonweso/Documents/Forge 2.0/scripts/run_nvidia_local.sh`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/pages/HomePage.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/pages/ChatPage.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/components/LeftPanel.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/components/ChatBox.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/components/PlanPanel.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/components/SearchModal.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/components/ForgeModelDropdown.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/pages/AgentsPage.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/pages/LibraryPage.vue`
- `/Users/carsonweso/Documents/Forge 2.0/frontend/src/pages/IntegrationsPage.vue`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/application/services/agent_service.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/domain/services/agent_domain_service.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/domain/services/agent_task_runner.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/domain/services/prompts/system.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/domain/services/prompts/execution.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/infrastructure/external/browser/browser_use_browser.py`
- `/Users/carsonweso/Documents/Forge 2.0/backend/app/infrastructure/external/browser/playwright_browser.py`

## Known Limitations Still True

- backend production hosting is still temporary
- some legacy internal naming from the imported Manus codebase may still remain
- persistent memory is not yet a full embeddings-based retrieval memory system
- integrations are not all fully authenticated production connectors yet
- live site reliability depends on the local backend tunnel until permanent hosting is set up

## Maintenance Rule For Future Work

Whenever Forge changes, update this file with:
- what changed
- why it changed
- whether it affects local only or live too
- any new URLs, env assumptions, or deployment notes

Last updated:
- 2026-04-06
