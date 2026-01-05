/**
 * Beta User Creation Script
 * 
 * Usage:
 *   SUPABASE_URL=https://xxx.supabase.co \
 *   SUPABASE_SERVICE_ROLE_KEY=your-key \
 *   node scripts/create-beta-users.js
 * 
 * Or update .env and run:
 *   node --env-file=.env scripts/create-beta-users.js
 */

const { createClient } = require('@supabase/supabase-js');

// Configuration
const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error('Error: Missing environment variables');
  console.error('Required: SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL), SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

// Create admin client
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
});

// =============================================================================
// BETA USERS TO CREATE
// =============================================================================
// Customize this list for your beta users

const BETA_USERS = [
  {
    email: 'student1@example.com',
    password: 'BetaStudent1!',
    role: 'student',
    first_name: 'Test',
    last_name: 'Student1',
  },
  {
    email: 'student2@example.com',
    password: 'BetaStudent2!',
    role: 'student',
    first_name: 'Test',
    last_name: 'Student2',
  },
  {
    email: 'coach@example.com',
    password: 'BetaCoach1!',
    role: 'coach',
    first_name: 'Test',
    last_name: 'Coach',
  },
  {
    email: 'admin@example.com',
    password: 'BetaAdmin1!',
    role: 'admin',
    first_name: 'Test',
    last_name: 'Admin',
  },
];

// =============================================================================
// MAIN
// =============================================================================

async function createUsers() {
  console.log('🚀 Creating beta users...\n');
  
  const results = {
    created: [],
    failed: [],
    skipped: [],
  };

  for (const user of BETA_USERS) {
    process.stdout.write(`Creating ${user.email}... `);

    try {
      // Check if user already exists
      const { data: existingUsers } = await supabase.auth.admin.listUsers();
      const exists = existingUsers?.users?.some(u => u.email === user.email);

      if (exists) {
        console.log('⏭️  Already exists');
        results.skipped.push(user.email);
        continue;
      }

      // Create auth user
      const { data, error } = await supabase.auth.admin.createUser({
        email: user.email,
        password: user.password,
        email_confirm: true,
        user_metadata: {
          role: user.role,
          first_name: user.first_name,
          last_name: user.last_name,
        },
      });

      if (error) {
        console.log(`❌ Error: ${error.message}`);
        results.failed.push({ email: user.email, error: error.message });
        continue;
      }

      // Update profile with correct role
      const { error: profileError } = await supabase
        .from('profiles')
        .upsert({
          id: data.user.id,
          email: user.email,
          role: user.role,
          first_name: user.first_name,
          last_name: user.last_name,
          is_active: true,
        });

      if (profileError) {
        console.log(`⚠️  Created but profile error: ${profileError.message}`);
      } else {
        console.log('✅ Created');
      }

      results.created.push({
        email: user.email,
        password: user.password,
        role: user.role,
      });

    } catch (err) {
      console.log(`❌ Exception: ${err.message}`);
      results.failed.push({ email: user.email, error: err.message });
    }
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 Summary\n');

  if (results.created.length > 0) {
    console.log(`✅ Created (${results.created.length}):`);
    results.created.forEach(u => {
      console.log(`   ${u.email} | ${u.password} | ${u.role}`);
    });
    console.log('');
  }

  if (results.skipped.length > 0) {
    console.log(`⏭️  Skipped (${results.skipped.length}): ${results.skipped.join(', ')}\n`);
  }

  if (results.failed.length > 0) {
    console.log(`❌ Failed (${results.failed.length}):`);
    results.failed.forEach(f => {
      console.log(`   ${f.email}: ${f.error}`);
    });
    console.log('');
  }

  console.log('='.repeat(50));
  
  // Output credentials for copy-paste
  if (results.created.length > 0) {
    console.log('\n📋 Copy-paste credentials for users:\n');
    results.created.forEach(u => {
      console.log(`Email: ${u.email}`);
      console.log(`Password: ${u.password}`);
      console.log(`Role: ${u.role}`);
      console.log('---');
    });
  }
}

// Run
createUsers().catch(console.error);
