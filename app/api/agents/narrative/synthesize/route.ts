/**
 * IvyQuest v10.0 - Narrative Synthesis Agent API Route
 * POST /api/agents/narrative/synthesize
 *
 * Proxies to Python agent service for narrative synthesis using Jenny's Formula:
 * IDENTITY + APTITUDE + PASSION + SERVICE = UNIQUE NARRATIVE
 *
 * Returns:
 * - brand_statement: One powerful sentence (15-25 words)
 * - narrative_dna: 2-3 paragraph personalized story
 * - first_principle: The core "why" driving the student
 * - themes: Key recurring themes
 * - confidence: Synthesis confidence (handoff if < 0.7)
 */

import { NextRequest, NextResponse } from 'next/server';

const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL || 'http://localhost:8001';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { profile_id, assessment_contract } = body;

    if (!profile_id) {
      return NextResponse.json(
        { success: false, error: 'profile_id is required' },
        { status: 400 }
      );
    }

    // Check if agents are enabled
    if (process.env.ENABLE_AGENTS !== 'true') {
      return NextResponse.json(
        { success: false, error: 'Agents are disabled. Set ENABLE_AGENTS=true' },
        { status: 503 }
      );
    }

    // Proxy to agent service
    const response = await fetch(`${AGENT_SERVICE_URL}/agents/narrative/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ profile_id, assessment_contract }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Narrative Synthesis Agent] Error:', errorText);
      return NextResponse.json(
        { success: false, error: `Agent service error: ${response.status}` },
        { status: response.status }
      );
    }

    const result = await response.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('[Narrative Synthesis Agent] Exception:', error);

    // Check if it's a connection error (agent service not running)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return NextResponse.json(
        {
          success: false,
          error: 'Agent service is not running. Start with: cd agents && python main.py',
        },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
