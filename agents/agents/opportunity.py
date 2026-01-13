# Opportunity Agent - Backward Compatibility Shim
# File: agents/agents/opportunity.py
#
# DEPRECATED: This module is maintained for backward compatibility.
# Use agents.programs.ProgramsAgent for new code.
#
# The OpportunityAgent has been renamed to ProgramsAgent and enhanced
# with Strategic Intelligence integration (v1.0.0).

"""
Backward compatibility shim for OpportunityAgent.

The Opportunity Agent has been renamed to Programs Agent and enhanced
with strategic intelligence features including:
- Archetype filtering (MIN_ARCHETYPE_FIT = 0.3)
- Identity synthesis integration
- Win cascade sequencing
- Program synergy recommendations

For new code, import from agents.programs:
    from agents.programs import ProgramsAgent, programs_agent

This shim re-exports the aliases for backward compatibility:
    from agents.opportunity import OpportunityAgent  # Still works
"""

from .programs import (
    ProgramsAgent,
    programs_agent,
    OpportunityAgent,
    opportunity_agent,
)

__all__ = [
    "ProgramsAgent",
    "programs_agent",
    "OpportunityAgent",
    "opportunity_agent",
]
