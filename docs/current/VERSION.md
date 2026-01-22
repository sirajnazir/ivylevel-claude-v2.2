# IvyLevel Version History

**Current Production Version:** v10.0
**Last Updated:** January 21, 2026

---

## Current: v10.0 - Proactive Autonomy (January 2026)

### Features
- **Proactive Opportunity Matching** - Automatically matches students to awards/programs
- **Deadline Monitoring** - Alerts for approaching deadlines
- **Stall Detection** - Identifies stuck projects
- **Inactivity Checks** - Re-engages inactive students

### Technical Changes
- Added `/agents/proactive/` module
- Added `/proactive/` API routes
- Migration 043: proactive_autonomy_tables
- 6 new database tables (nudge_queue, proactive_notifications, etc.)

### Configuration
```bash
PROACTIVE_ENABLED=true
PROACTIVE_OPPORTUNITY_MATCH=true
PROACTIVE_DEADLINE_ALERTS=true
PROACTIVE_STALL_DETECTION=true
PROACTIVE_INACTIVITY_CHECK=true
```

---

## Previous Versions

### v9.0 - Middleware Integration (January 2026)
- 50 middleware patterns implemented
- Quality scoring system
- Audit trails for agent actions
- Coaching assets (E1-E22 techniques)

### v5.4 - Execution Chat Enhancement (January 2026)
- Game plan context in system prompt
- 13 execution coaching tools
- EDS (Execution Distress Score) tracking
- Weekly plan generation

### v5.0 - Multi-Agent Architecture (January 2026)
- ReAct cycles for sub-agents
- LangChain/Agno integration
- Orchestrator pattern
- Agent-specific memory

### v4.0 - Assessment Frames (December 2025)
- 6-frame assessment flow
- Profile scoring engine
- Archetype detection
- Spike narrative generation

### v3.0 - Game Plan Generation (December 2025)
- 4-year strategic roadmaps
- Project-based planning
- Award/program integration

### v2.0 - Dashboard MVP (December 2025)
- Multi-tab dashboard
- Profile management
- Basic chat interface

### v1.0 - Foundation (November 2025)
- Initial Next.js setup
- Supabase integration
- Basic authentication

---

## Upcoming: v11.0 (Post-Launch)

### Planned Features
- **Proactive Notifications UI** - Display matches in dashboard
- **Enhanced Memory Display** - Show what Jenny remembers
- **Outcome Tracking** - Win/loss learning system
- **Letta Evaluation** - Assess advanced memory needs

### Candidates for v11.0
- A2A (Agent-to-Agent) communication
- Cross-session memory persistence
- Parent/counselor portal
- Mobile responsive improvements

---

## Version Naming Convention

| Version | Type | Example |
|---------|------|---------|
| X.0 | Major release | v10.0 - Proactive Autonomy |
| X.Y | Feature update | v10.1 - Notification UI |
| X.Y.Z | Bug fix | v10.0.1 - Schema fix |

---

## Rollback Procedures

### Code Rollback
```bash
# View recent commits
git log --oneline -10

# Rollback to specific version
git checkout <commit-hash>

# Or revert specific commit
git revert <commit-hash>
```

### Database Rollback
- Migrations are forward-only in Supabase
- For critical rollbacks, restore from backup
- Contact Supabase support for point-in-time recovery

---

## Changelog Location

Detailed changes for each version are tracked in:
- Git commit history
- `_archive/docs/iterations/` - Old version specs
- LangSmith traces - Runtime behavior changes
