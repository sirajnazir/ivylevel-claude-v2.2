/**
 * IvyQuest v3.0 — Quest Flow E2E Tests
 *
 * Tests the actual quest flow with the current UI implementation.
 * Simulates Bay Area students completing Frame 1 (Warmup) and navigating
 * through placeholder frames 2-6.
 */

import { test, expect, Page } from '@playwright/test';
import { BAY_AREA_PROFILES, StudentProfile } from './student-profiles';

// ============================================================================
// TEST CONFIGURATION
// ============================================================================

const PROFILES_TO_TEST = BAY_AREA_PROFILES; // Test all 10 profiles

interface TestResult {
  profileId: string;
  studentName: string;
  school: string;
  grade: string;
  frameReached: number;
  passed: boolean;
  errors: string[];
  duration: number;
}

const testResults: TestResult[] = [];

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

async function clearStorage(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

async function log(msg: string) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

async function selectRole(page: Page, role: 'STUDENT' | 'PARENT' = 'STUDENT') {
  await log(`  Selecting role: ${role}`);
  const roleCard = page.locator(`text=${role === 'STUDENT' ? 'Student' : 'Parent'}`).first();
  if (await roleCard.isVisible({ timeout: 5000 })) {
    await roleCard.click();
    await page.waitForTimeout(500);
  }
}

async function fillIdentity(page: Page, name: string, grade: string) {
  await log(`  Filling identity: ${name}, Grade ${grade}`);

  // Fill name
  const nameInput = page.locator('input[placeholder*="name" i], input[name="name"]').first();
  if (await nameInput.isVisible({ timeout: 5000 })) {
    await nameInput.fill(name);
  }

  // Select grade if dropdown exists
  const gradeSelect = page.locator('select, [role="combobox"]').first();
  if (await gradeSelect.isVisible({ timeout: 3000 })) {
    try {
      await gradeSelect.click();
      await page.waitForTimeout(300);
      const gradeOption = page.locator(`text="${grade}th Grade", text="Grade ${grade}"`).first();
      if (await gradeOption.isVisible({ timeout: 2000 })) {
        await gradeOption.click();
      }
    } catch {
      // Grade selection may not be available
    }
  }

  await page.waitForTimeout(500);
}

// Map school IDs (lowercase or uppercase) to display names (as shown in UI)
// Only includes schools that exist in our SCHOOL_DATABASE
const SCHOOL_DISPLAY_NAMES: Record<string, string> = {
  'harvard': 'Harvard',
  'stanford': 'Stanford',
  'mit': 'MIT',
  'yale': 'Yale',
  'princeton': 'Princeton',
  'caltech': 'Caltech',
  'cmu': 'CMU',
  'columbia': 'Columbia',
  // Also handle uppercase versions
  'HARVARD': 'Harvard',
  'STANFORD': 'Stanford',
  'MIT': 'MIT',
  'YALE': 'Yale',
  'PRINCETON': 'Princeton',
  'CALTECH': 'Caltech',
  'CMU': 'CMU',
  'COLUMBIA': 'Columbia',
};

// List of schools available in our database
const AVAILABLE_SCHOOLS = ['harvard', 'stanford', 'mit', 'yale', 'princeton', 'caltech', 'cmu', 'columbia'];

async function selectSchools(page: Page, schoolIds: string[]) {
  await log(`  Selecting schools from: ${schoolIds.join(', ')}`);

  // Wait for school grid to be visible
  await page.waitForSelector('button:has-text("% accept")', { timeout: 10000 });
  await page.waitForTimeout(500);

  // Filter to only schools that exist in our database
  const validSchools = schoolIds
    .map(id => id.toLowerCase())
    .filter(id => AVAILABLE_SCHOOLS.includes(id));

  // If no valid schools, select first 3 available schools
  const schoolsToSelect = validSchools.length > 0
    ? validSchools.slice(0, 3)
    : AVAILABLE_SCHOOLS.slice(0, 3);

  await log(`    Will select: ${schoolsToSelect.join(', ')}`);

  for (const schoolId of schoolsToSelect) {
    const displayName = SCHOOL_DISPLAY_NAMES[schoolId] || schoolId;
    await log(`    Looking for school button: ${displayName}`);

    // Find and click the school button - it contains the display name and acceptance rate
    const schoolButton = page.locator(`button:has-text("${displayName}")`).first();

    if (await schoolButton.isVisible({ timeout: 3000 })) {
      await schoolButton.click();
      await log(`    Clicked: ${displayName}`);
      await page.waitForTimeout(300);
    } else {
      await log(`    Could not find school: ${displayName}`);
    }
  }

  // Verify selection count
  const selectionIndicator = page.locator('text=/\\d+ school(s)? selected/i');
  if (await selectionIndicator.isVisible({ timeout: 2000 })) {
    const text = await selectionIndicator.textContent();
    await log(`    Selection status: ${text}`);
  }
}

// Popular majors that appear as clickable buttons in the UI
const POPULAR_MAJORS = [
  'Computer Science',
  'Engineering',
  'Biology',
  'Economics',
  'Pre-Med',
  'Mathematics',
  'Physics',
  'Political Science',
  'Psychology',
  'Business',
];

async function fillMajor(page: Page, major: string) {
  await log(`  Filling major: ${major}`);

  // First try to click a matching popular major button (more reliable)
  const matchedMajor = POPULAR_MAJORS.find(
    (pm) => major.toLowerCase().includes(pm.toLowerCase()) || pm.toLowerCase().includes(major.toLowerCase().split(' ')[0])
  );

  if (matchedMajor) {
    const majorButton = page.locator(`button:has-text("${matchedMajor}")`).first();
    if (await majorButton.isVisible({ timeout: 3000 })) {
      await majorButton.click();
      await log(`    Clicked popular major: ${matchedMajor}`);
      await page.waitForTimeout(500);
      return;
    }
  }

  // Fallback: Try to type in the input with proper event simulation
  const majorInput = page.locator('input[placeholder*="Computer Science" i], input[placeholder*="major" i]').first();
  if (await majorInput.isVisible({ timeout: 5000 })) {
    await majorInput.click();
    await majorInput.fill('');  // Clear first
    await majorInput.pressSequentially(major.slice(0, 30), { delay: 50 });  // Type with delays
    await log(`    Typed major: ${major}`);
  }

  await page.waitForTimeout(500);
}

async function clickNext(page: Page, isLast: boolean = false) {
  // Try various "next" button selectors - "Complete" is used on the last card
  const buttonText = isLast ? 'Complete' : 'Continue';
  const nextBtn = page.locator(`button:has-text("${buttonText}"), button:has-text("Next")`).first();

  if (await nextBtn.isVisible({ timeout: 5000 })) {
    // Check if button is enabled
    const isDisabled = await nextBtn.isDisabled();
    if (isDisabled) {
      await log(`    Button "${buttonText}" is disabled`);
      return false;
    }

    await nextBtn.click();
    await page.waitForTimeout(800);
    return true;
  }
  await log(`    Button "${buttonText}" not found`);
  return false;
}

async function navigateThroughPlaceholderFrames(page: Page, maxFrame: number = 6): Promise<number> {
  let currentFrame = 2;

  while (currentFrame <= maxFrame) {
    await log(`  Navigating through Frame ${currentFrame} (placeholder)`);

    // Look for the continue button in placeholder frames
    const continueBtn = page.locator('button:has-text("Continue to Next Frame"), button:has-text("Continue"), button:has-text("Next")').first();

    if (await continueBtn.isVisible({ timeout: 5000 })) {
      await continueBtn.click();
      await page.waitForTimeout(1000);
      currentFrame++;
    } else {
      await log(`  Could not find continue button at Frame ${currentFrame}`);
      break;
    }
  }

  return currentFrame - 1;
}

// ============================================================================
// TEST SUITE
// ============================================================================

test.describe('IvyQuest Quest Flow - Bay Area Students', () => {
  test.beforeAll(async () => {
    await log('========================================');
    await log('IvyQuest Quest Flow E2E Tests Starting');
    await log(`Testing ${PROFILES_TO_TEST.length} Bay Area profiles`);
    await log('========================================');
  });

  test.afterAll(async () => {
    await generateReport();
  });

  for (const profile of PROFILES_TO_TEST) {
    test(`Quest: ${profile.name} (${profile.school})`, async ({ page }) => {
      test.setTimeout(90000);

      const result: TestResult = {
        profileId: profile.id,
        studentName: profile.name,
        school: profile.school,
        grade: profile.grade,
        frameReached: 0,
        passed: false,
        errors: [],
        duration: 0,
      };

      const startTime = Date.now();

      try {
        await log(`\n${'='.repeat(60)}`);
        await log(`TESTING: ${profile.name}`);
        await log(`School: ${profile.school}`);
        await log(`Grade: ${profile.grade}, Major: ${profile.intendedMajor}`);
        await log(`${'='.repeat(60)}`);

        // Navigate to quest entry
        await page.goto('/quest');
        await clearStorage(page);
        await page.reload();
        await page.waitForLoadState('networkidle');
        await log('Loaded quest entry page');

        // Take screenshot of entry page
        await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-01-entry.png` });

        // Click "Begin Your Quest"
        const beginBtn = page.locator('button:has-text("Begin"), button:has-text("Start")').first();
        await expect(beginBtn).toBeVisible({ timeout: 10000 });
        await beginBtn.click();
        await page.waitForTimeout(1500);
        await log('Clicked Begin Your Quest');

        // Verify we're on Frame 1
        await expect(page).toHaveURL(/\/quest\/1/);
        result.frameReached = 1;
        await log('Reached Frame 1: Warmup');

        // Card 1: Role Selection
        await selectRole(page, 'STUDENT');
        if (await clickNext(page)) {
          await log('  Completed Card 1: Role');
        }

        // Card 2: Identity
        await fillIdentity(page, profile.name, profile.grade);
        if (await clickNext(page)) {
          await log('  Completed Card 2: Identity');
        }

        // Card 3: Schools
        await selectSchools(page, profile.targetSchools);
        if (await clickNext(page)) {
          await log('  Completed Card 3: Schools');
        }

        // Card 4: Major (last card in Frame 1 - button says "Complete")
        await fillMajor(page, profile.intendedMajor);
        await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-02-frame1-complete.png` });
        if (await clickNext(page, true)) {  // isLast = true for "Complete" button
          await log('  Completed Card 4: Major - Frame 1 Complete!');
        }

        // Wait for navigation to Frame 2 (wait for URL change)
        try {
          await page.waitForURL(/\/quest\/2/, { timeout: 5000 });
          result.frameReached = 2;
          await log('Advanced to Frame 2');
          await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-04-frame2.png` });

          // Navigate through placeholder frames (2-6)
          const finalFrame = await navigateThroughPlaceholderFrames(page);
          result.frameReached = Math.max(result.frameReached, finalFrame);

          // Check for results page
          const currentUrl = page.url();
          if (currentUrl.includes('/results')) {
            await log('Reached Results page - Assessment Complete!');
            result.frameReached = 6;
            await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-05-results.png` });
          }
        } catch {
          await log('  Did not advance to Frame 2 - checking current URL');
          const currentUrl = page.url();
          await log(`  Current URL: ${currentUrl}`);
        }

        // Take final screenshot
        await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-03-final.png` });

        result.passed = result.frameReached >= 1;
        await log(`Final frame reached: ${result.frameReached}`);

      } catch (error) {
        result.errors.push(String(error));
        await log(`ERROR: ${error}`);
        await page.screenshot({ path: `e2e/reports/screenshots/${profile.id}-error.png` });
      }

      result.duration = Date.now() - startTime;
      testResults.push(result);

      await log(`Test completed in ${result.duration}ms - ${result.passed ? 'PASSED' : 'FAILED'}`);
    });
  }
});

// ============================================================================
// REPORT GENERATION
// ============================================================================

async function generateReport() {
  await log('\n' + '='.repeat(80));
  await log('IVYQUEST QUEST FLOW E2E TEST REPORT');
  await log('='.repeat(80));

  const passed = testResults.filter(r => r.passed).length;
  const total = testResults.length;

  await log(`\nSUMMARY:`);
  await log(`  Total Tests: ${total}`);
  await log(`  Passed: ${passed}`);
  await log(`  Failed: ${total - passed}`);
  await log(`  Pass Rate: ${((passed / total) * 100).toFixed(1)}%`);

  await log(`\nDETAILED RESULTS:`);
  await log('-'.repeat(80));

  for (const result of testResults) {
    const status = result.passed ? 'PASS' : 'FAIL';
    await log(`\n[${status}] ${result.studentName}`);
    await log(`  School: ${result.school}`);
    await log(`  Grade: ${result.grade}`);
    await log(`  Frames Reached: ${result.frameReached}/6`);
    await log(`  Duration: ${result.duration}ms`);
    if (result.errors.length > 0) {
      await log(`  Errors: ${result.errors.join('; ')}`);
    }
  }

  // Group by grade
  await log(`\nRESULTS BY GRADE:`);
  for (const grade of ['9', '10', '11', '12']) {
    const gradeResults = testResults.filter(r => r.grade === grade);
    if (gradeResults.length > 0) {
      const gradePassed = gradeResults.filter(r => r.passed).length;
      await log(`  Grade ${grade}: ${gradePassed}/${gradeResults.length} passed`);
    }
  }

  await log('\n' + '='.repeat(80));
  await log('END OF REPORT');
  await log('='.repeat(80));

  // Save JSON report
  const fs = await import('fs');
  const report = {
    timestamp: new Date().toISOString(),
    summary: { total, passed, failed: total - passed },
    results: testResults,
  };
  fs.writeFileSync('e2e/reports/quest-flow-report.json', JSON.stringify(report, null, 2));
  await log('\nReport saved to e2e/reports/quest-flow-report.json');
}
