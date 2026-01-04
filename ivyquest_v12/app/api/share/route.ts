/**
 * Share API Route
 * Generates shareable links for "Share with Parent" functionality.
 * @version 10.0
 */

import { NextRequest, NextResponse } from 'next/server';
import { nanoid } from 'nanoid';

// In-memory store for demo (use Redis/database in production)
const shareLinks = new Map<string, ShareData>();

interface ShareData {
  id: string;
  studentName: string;
  profileSnapshot: any;
  scores: {
    overall: number;
    cri: number;
    categories: {
      aptitude: number;
      passion: number;
      service: number;
      identity: number;
    };
  };
  narrativeDna?: string;
  archetype?: string;
  topActions?: Array<{ title: string; priority: string }>;
  createdAt: string;
  expiresAt: string;
  viewCount: number;
  maxViews: number;
}

/**
 * POST /api/share
 * Creates a new shareable link.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      studentName,
      profile,
      scores,
      narrativeDna,
      archetype,
      topActions,
      expiresInHours = 72,
      maxViews = 10,
    } = body;

    if (!studentName || !scores) {
      return NextResponse.json(
        { error: 'Missing required fields: studentName, scores' },
        { status: 400 }
      );
    }

    const shareId = nanoid(12);
    const now = new Date();
    const expiresAt = new Date(now.getTime() + expiresInHours * 60 * 60 * 1000);

    const shareData: ShareData = {
      id: shareId,
      studentName,
      profileSnapshot: sanitizeProfile(profile),
      scores: {
        overall: scores.overall,
        cri: scores.cri || 1.0,
        categories: scores.categories || {
          aptitude: 0,
          passion: 0,
          service: 0,
          identity: 0,
        },
      },
      narrativeDna,
      archetype,
      topActions: topActions?.slice(0, 5),
      createdAt: now.toISOString(),
      expiresAt: expiresAt.toISOString(),
      viewCount: 0,
      maxViews,
    };

    shareLinks.set(shareId, shareData);

    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://ivyquest.ivylevel.com';
    const shareUrl = `${baseUrl}/share/${shareId}`;

    return NextResponse.json({
      success: true,
      shareId,
      shareUrl,
      expiresAt: expiresAt.toISOString(),
      maxViews,
    });
  } catch (error) {
    console.error('Share API error:', error);
    return NextResponse.json(
      { error: 'Failed to create share link' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/share?id={shareId}
 * Retrieves share data for viewing.
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const shareId = searchParams.get('id');

    if (!shareId) {
      return NextResponse.json(
        { error: 'Share ID is required' },
        { status: 400 }
      );
    }

    const shareData = shareLinks.get(shareId);

    if (!shareData) {
      return NextResponse.json(
        { error: 'Share link not found or expired' },
        { status: 404 }
      );
    }

    if (new Date() > new Date(shareData.expiresAt)) {
      shareLinks.delete(shareId);
      return NextResponse.json(
        { error: 'Share link has expired' },
        { status: 410 }
      );
    }

    if (shareData.viewCount >= shareData.maxViews) {
      return NextResponse.json(
        { error: 'Share link has reached maximum views' },
        { status: 410 }
      );
    }

    shareData.viewCount += 1;
    shareLinks.set(shareId, shareData);

    return NextResponse.json({
      success: true,
      data: {
        studentName: shareData.studentName,
        scores: shareData.scores,
        narrativeDna: shareData.narrativeDna,
        archetype: shareData.archetype,
        topActions: shareData.topActions,
        createdAt: shareData.createdAt,
        viewsRemaining: shareData.maxViews - shareData.viewCount,
      },
    });
  } catch (error) {
    console.error('Share GET error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve share data' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/share?id={shareId}
 * Revokes a share link.
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const shareId = searchParams.get('id');

    if (!shareId) {
      return NextResponse.json(
        { error: 'Share ID is required' },
        { status: 400 }
      );
    }

    const existed = shareLinks.delete(shareId);

    return NextResponse.json({
      success: true,
      deleted: existed,
    });
  } catch (error) {
    console.error('Share DELETE error:', error);
    return NextResponse.json(
      { error: 'Failed to delete share link' },
      { status: 500 }
    );
  }
}

function sanitizeProfile(profile: any): any {
  if (!profile) return null;
  return {
    identity: {
      name: profile.identity?.name,
      grade: profile.identity?.grade,
    },
    aptitude: {
      gpa_unweighted: profile.aptitude?.gpa_unweighted,
    },
    passion: {
      ec_count: profile.passion?.ec_types?.length || 0,
      leadership_level: profile.passion?.leadership_level,
    },
  };
}
