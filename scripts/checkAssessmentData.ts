/**
 * Database Inspection Script
 * Checks if the new 4-pillar assessment data was saved correctly
 */

import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function checkAssessmentData() {
  console.log('\n=== Assessment Data Inspection ===\n');

  // Get most recent profile (by updated_at)
  const { data: profiles, error: profileError } = await supabase
    .from('profiles')
    .select('*')
    .order('updated_at', { ascending: false })
    .limit(1);

  if (profileError) {
    console.error('Error fetching profiles:', profileError);
    return;
  }

  if (!profiles || profiles.length === 0) {
    console.log('No profiles found');
    return;
  }

  const profile = profiles[0];
  console.log('📊 Profile ID:', profile.id);
  console.log('📧 Email:', profile.email || 'N/A');
  console.log('🕐 Updated:', new Date(profile.updated_at).toLocaleString());
  console.log('✅ Completed:', profile.is_completed || false);
  console.log('\n--- Assessment Data ---');

  // Check Identity Pillar
  console.log('\n🔷 IDENTITY PILLAR:');
  console.log('  Name:', profile.name || 'N/A');
  console.log('  Grade:', profile.grade || 'N/A');
  console.log('  Role:', profile.role || 'N/A');

  // Check Aptitude Pillar
  console.log('\n🔶 APTITUDE PILLAR:');
  console.log('  GPA Weighted:', profile.gpa_weighted || 'N/A');
  console.log('  GPA Unweighted:', profile.gpa_unweighted || 'N/A');
  console.log('  SAT Total:', profile.sat_total || 'N/A');
  console.log('  ACT Total:', profile.act_total || 'N/A');
  console.log('  AP Count:', profile.ap_count || 'N/A');
  console.log('  Test Optional:', profile.test_optional || false);

  // Check Passion Pillar
  console.log('\n❤️  PASSION PILLAR:');
  console.log('  Spike Category:', profile.spike_category || 'N/A');
  console.log('  Leadership Level:', profile.leadership_level || 'N/A');
  console.log('  EC Commitment Years:', profile.ec_commitment_years || 'N/A');
  console.log('  EC Hours Weekly:', profile.ec_hours_weekly || 'N/A');
  console.log('  Research Level:', profile.research_level || 'N/A');

  // NEW: Check WHY fields (4-pillar update)
  console.log('\n  🆕 WHY Fields:');
  console.log('    Why Passion:', profile.why_passion ? `"${profile.why_passion.substring(0, 50)}..."` : 'N/A');
  console.log('    Passion Origin:', profile.passion_origin || 'N/A');
  console.log('    Passion Reason:', profile.passion_reason || 'N/A');

  // Check Community Pillar
  console.log('\n💚 COMMUNITY PILLAR:');
  console.log('  Service Leadership:', profile.service_leadership || 'N/A');
  console.log('  Service Hours:', profile.service_hours || 'N/A');
  console.log('  Community Impact:', profile.community_impact || 'N/A');

  // Check Operating Data (Frame 4)
  console.log('\n⚙️  OPERATING DATA (Frame 4):');
  console.log('  First Gen:', profile.first_generation !== null ? profile.first_generation : 'N/A');
  console.log('  Work Hours:', profile.work_hours || 'N/A');
  console.log('  Parent 1 Occupation:', profile.parent1_occupation || 'N/A');
  console.log('  Parent 2 Occupation:', profile.parent2_occupation || 'N/A');
  console.log('  Parent 1 Education:', profile.parent1_education || 'N/A');
  console.log('  Transportation:', profile.transportation || 'N/A');
  console.log('  Languages Spoken:', profile.languages_spoken || 'N/A');

  // Check Target Schools
  console.log('\n🎓 TARGET SCHOOLS:');
  const targetSchools = profile.target_schools || [];
  if (targetSchools.length > 0) {
    targetSchools.forEach((school: string, idx: number) => {
      console.log(`  ${idx + 1}. ${school}`);
    });
  } else {
    console.log('  None selected');
  }

  // Check sessions table
  console.log('\n\n=== Session Data ===\n');
  const { data: sessions, error: sessionError } = await supabase
    .from('sessions')
    .select('*')
    .eq('user_id', profile.id)
    .order('created_at', { ascending: false })
    .limit(1);

  if (sessionError) {
    console.error('Error fetching sessions:', sessionError);
  } else if (sessions && sessions.length > 0) {
    const session = sessions[0];
    console.log('📋 Session ID:', session.id);
    console.log('🎯 Current Frame:', session.current_frame || 'N/A');
    console.log('✅ Completed:', session.is_completed || false);
    console.log('🕐 Started:', new Date(session.created_at).toLocaleString());
    console.log('🏁 Completed At:', session.completed_at ? new Date(session.completed_at).toLocaleString() : 'N/A');
  } else {
    console.log('No session found');
  }

  // Check assessment_results table
  console.log('\n\n=== Assessment Results (Scoring) ===\n');
  const { data: results, error: resultsError } = await supabase
    .from('assessment_results')
    .select('*')
    .eq('profile_id', profile.id)
    .order('created_at', { ascending: false })
    .limit(1);

  if (resultsError) {
    console.error('Error fetching results:', resultsError);
  } else if (results && results.length > 0) {
    const result = results[0];
    console.log('📊 Total Score:', result.total_score || 'N/A');
    console.log('📈 Percentile:', result.percentile_rank || 'N/A');
    console.log('🎯 Archetype:', result.archetype || 'N/A');
    console.log('\n  Category Scores:');
    console.log('    Aptitude:', result.score_aptitude || 'N/A');
    console.log('    Passion:', result.score_passion || 'N/A');
    console.log('    Community:', result.score_community || 'N/A');
    console.log('    Narrative:', result.score_narrative || 'N/A');
    console.log('\n  Top School Probability:', result.top_school_probability || 'N/A');
  } else {
    console.log('No assessment results found');
  }

  console.log('\n\n=== Analysis Summary ===\n');

  // Check if new 4-pillar fields exist
  const hasNewWHYFields = !!(profile.why_passion || profile.passion_origin || profile.passion_reason);
  const hasOperatingData = !!(profile.first_generation !== null || profile.work_hours || profile.parent1_occupation);
  const hasTargetSchools = targetSchools.length > 0;

  console.log('✅ New WHY fields (4-pillar):', hasNewWHYFields ? 'PRESENT' : '❌ MISSING');
  console.log('✅ Operating Data (Frame 4):', hasOperatingData ? 'PRESENT' : '❌ MISSING');
  console.log('✅ Target Schools:', hasTargetSchools ? 'PRESENT' : '❌ MISSING');
  console.log('✅ Assessment Completed:', profile.is_completed ? 'YES' : '❌ NO');

  if (results && results.length > 0) {
    console.log('✅ Scoring Engine Ran:', 'YES');
  } else {
    console.log('❌ Scoring Engine Ran:', 'NO - Results not found');
  }

  console.log('\n');
}

checkAssessmentData()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error('Script error:', err);
    process.exit(1);
  });
