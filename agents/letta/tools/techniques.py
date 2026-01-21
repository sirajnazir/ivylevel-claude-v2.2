"""
Techniques Bridge Tools
=======================

Bridge tools that connect Letta agents to the existing AssetSelector
for accessing 139 coaching techniques.

These tools wrap the existing AssetSelector methods without modifying them.
"""

import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID

logger = structlog.get_logger()


# Letta tool definitions for registration
TECHNIQUE_TOOLS = [
    {
        "name": "search_techniques",
        "description": "Search for coaching techniques relevant to a given context. Returns techniques from the 139-technique library organized by domain (Assessment A1-A12, Extracurriculars B1-B18, Essays C1-C25, Awards D1-D20, Execution E1-E22).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language description of what you're trying to help with",
                },
                "domain": {
                    "type": "string",
                    "enum": ["assessment", "extracurriculars", "essay", "awards", "execution", "strategy"],
                    "description": "The coaching domain to search within",
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum number of techniques to return",
                },
            },
            "required": ["query", "domain"],
        },
    },
    {
        "name": "get_technique_by_id",
        "description": "Get a specific technique by its ID (e.g., A1, B5, C12, D3, E7).",
        "parameters": {
            "type": "object",
            "properties": {
                "technique_id": {
                    "type": "string",
                    "description": "The technique ID (e.g., A1, B5, C12)",
                },
            },
            "required": ["technique_id"],
        },
    },
    {
        "name": "get_top_techniques_for_domain",
        "description": "Get the most effective techniques for a specific domain based on usage statistics.",
        "parameters": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "enum": ["assessment", "extracurriculars", "essay", "awards", "execution", "strategy"],
                    "description": "The coaching domain",
                },
                "archetype": {
                    "type": "string",
                    "description": "Optional student archetype to filter by",
                },
                "limit": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum number of techniques to return",
                },
            },
            "required": ["domain"],
        },
    },
]


async def search_techniques(
    query: str,
    domain: str,
    limit: int = 5,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Search for coaching techniques relevant to a given context.

    This function bridges to the existing AssetSelector.select_techniques() method.

    Args:
        query: Natural language description of the coaching need
        domain: Coaching domain (assessment, extracurriculars, essay, awards, execution, strategy)
        limit: Maximum number of techniques to return
        supabase_client: Supabase client (optional, will create if not provided)

    Returns:
        Dictionary with techniques and metadata
    """
    try:
        # Import existing intelligence layer
        from intelligence.registry import AssetSelector, AssetRegistry
        from intelligence.primitives import AssetDomain

        # Map domain string to enum
        domain_map = {
            "assessment": AssetDomain.ASSESSMENT,
            "extracurriculars": AssetDomain.EXTRACURRICULARS,
            "essay": AssetDomain.ESSAY,
            "awards": AssetDomain.AWARDS,
            "execution": AssetDomain.EXECUTION,
            "strategy": AssetDomain.STRATEGY,
        }

        asset_domain = domain_map.get(domain.lower())
        if not asset_domain:
            return {
                "success": False,
                "error": f"Unknown domain: {domain}. Valid domains: {list(domain_map.keys())}",
                "techniques": [],
            }

        # Get or create registry
        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        registry = AssetRegistry(supabase_client)
        selector = AssetSelector(registry)

        # Use existing select_techniques method
        techniques = await selector.select_techniques(
            context=query,
            domain=asset_domain,
            limit=limit,
        )

        # Format response
        technique_list = []
        for tech in techniques:
            technique_list.append({
                "id": tech.content.get("technique_id", ""),
                "name": tech.name,
                "description": tech.description,
                "when_to_use": tech.content.get("when_to_use", ""),
                "key_steps": tech.content.get("key_steps", [])[:3],
                "tags": tech.tags[:5],
            })

        logger.info(
            "letta_search_techniques",
            query=query[:50],
            domain=domain,
            results=len(technique_list),
        )

        return {
            "success": True,
            "query": query,
            "domain": domain,
            "techniques": technique_list,
            "count": len(technique_list),
        }

    except ImportError as e:
        logger.error("letta_techniques_import_error", error=str(e))
        return {
            "success": False,
            "error": "Intelligence layer not available",
            "techniques": [],
        }
    except Exception as e:
        logger.error("letta_search_techniques_error", error=str(e))
        return {
            "success": False,
            "error": str(e),
            "techniques": [],
        }


async def get_technique_by_id(
    technique_id: str,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get a specific technique by its ID.

    Args:
        technique_id: The technique ID (e.g., A1, B5, C12)
        supabase_client: Supabase client (optional)

    Returns:
        Dictionary with technique details or error
    """
    try:
        from intelligence.registry import AssetRegistry
        from intelligence.primitives import AssetType

        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        registry = AssetRegistry(supabase_client)

        # Search by technique_id in content
        result = supabase_client.table("coaching_assets") \
            .select("*") \
            .eq("asset_type", AssetType.TECHNIQUE.value) \
            .execute()

        # Find matching technique
        for row in result.data or []:
            content = row.get("content", {})
            if content.get("technique_id") == technique_id.upper():
                return {
                    "success": True,
                    "technique": {
                        "id": technique_id.upper(),
                        "name": row.get("name", ""),
                        "description": row.get("description", ""),
                        "domain": row.get("domain", ""),
                        "when_to_use": content.get("when_to_use", ""),
                        "key_steps": content.get("key_steps", []),
                        "example_dialogue": content.get("example_dialogue", ""),
                        "tags": row.get("tags", []),
                    },
                }

        return {
            "success": False,
            "error": f"Technique {technique_id} not found",
            "technique": None,
        }

    except Exception as e:
        logger.error("letta_get_technique_error", technique_id=technique_id, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "technique": None,
        }


async def get_top_techniques_for_domain(
    domain: str,
    archetype: Optional[str] = None,
    limit: int = 5,
    supabase_client=None,
) -> Dict[str, Any]:
    """
    Get the most effective techniques for a domain.

    Args:
        domain: Coaching domain
        archetype: Optional student archetype to filter by
        limit: Maximum number of techniques
        supabase_client: Supabase client (optional)

    Returns:
        Dictionary with top techniques
    """
    try:
        from intelligence.registry import AssetRegistry
        from intelligence.primitives import AssetDomain

        domain_map = {
            "assessment": AssetDomain.ASSESSMENT,
            "extracurriculars": AssetDomain.EXTRACURRICULARS,
            "essay": AssetDomain.ESSAY,
            "awards": AssetDomain.AWARDS,
            "execution": AssetDomain.EXECUTION,
            "strategy": AssetDomain.STRATEGY,
        }

        asset_domain = domain_map.get(domain.lower())
        if not asset_domain:
            return {
                "success": False,
                "error": f"Unknown domain: {domain}",
                "techniques": [],
            }

        if supabase_client is None:
            from tools.database import get_supabase_client
            supabase_client = get_supabase_client()

        registry = AssetRegistry(supabase_client)

        # Get top effective techniques
        techniques = await registry.get_top_effective(
            domain=asset_domain,
            archetype=archetype,
            min_usage=1,
            limit=limit,
        )

        technique_list = []
        for tech in techniques:
            technique_list.append({
                "id": tech.content.get("technique_id", ""),
                "name": tech.name,
                "description": tech.description,
                "effectiveness": tech.effectiveness_score,
                "usage_count": tech.usage_count,
            })

        return {
            "success": True,
            "domain": domain,
            "archetype": archetype,
            "techniques": technique_list,
            "count": len(technique_list),
        }

    except Exception as e:
        logger.error("letta_top_techniques_error", domain=domain, error=str(e))
        return {
            "success": False,
            "error": str(e),
            "techniques": [],
        }
