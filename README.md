# Business Central Agent Knowledge Hub

Vendor-neutral routing catalog for agents that investigate Microsoft Dynamics 365 Business Central.

This repository does not mirror product documentation. It tells agents which source to use, how to qualify evidence, and when live-environment validation is required.

## Supported roles

- BC Support Lead
- BC Functional & Product Expert
- BC Technical Investigator
- BC TSI & Infrastructure Specialist
- BC Solution & Estimation Specialist
- Automation & Agent Designer

## Start here

Agents start at `AGENTS.md`, then load the matching file in `routing/`, the relevant domain file, and only the necessary source catalog and policies.

## Copilot Studio setup

1. Publish this repository publicly.
2. Add the repository root under **Knowledge > Public websites**.
3. Load the shared `bc-knowledge-routing` skill into every specialist agent.
4. In each agent mission, declare its role key exactly as listed in `AGENTS.md`.
5. Keep operational tools such as Azure DevOps MCP, Microsoft Learn MCP, BC Observatory MCP, Work IQ, Dataverse GET, or Business Central MCP attached to the agents that need them.

The Hub selects sources. The final source or live tool supplies the evidence.
