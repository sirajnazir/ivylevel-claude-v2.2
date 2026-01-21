-- ============================================
-- Migration 041: Fix Safe Date Parsing in Game Plan Trigger
-- ============================================
-- This fixes the error:
--   "invalid input syntax for type date: 'February-March for formal programs'"
--
-- The extract_goals_from_gameplan trigger was trying to cast deadline strings
-- like "Before junior year" or "February-March" directly to DATE, which fails.
--
-- Solution: Create a safe_to_date function that returns NULL for invalid dates.
-- ============================================

-- Create a safe date parsing function that returns NULL for invalid inputs
CREATE OR REPLACE FUNCTION safe_to_date(text_value TEXT)
RETURNS DATE AS $$
BEGIN
    -- Return NULL if input is empty or null
    IF text_value IS NULL OR text_value = '' THEN
        RETURN NULL;
    END IF;

    -- Try to parse as date
    -- Only accept proper date formats (YYYY-MM-DD, etc.)
    BEGIN
        -- First, check if it looks like a date (starts with a year or has proper structure)
        IF text_value ~ '^\d{4}-\d{2}-\d{2}' THEN
            RETURN text_value::DATE;
        ELSIF text_value ~ '^\d{1,2}/\d{1,2}/\d{4}$' THEN
            -- Handle MM/DD/YYYY format
            RETURN to_date(text_value, 'MM/DD/YYYY');
        ELSIF text_value ~ '^\d{4}/\d{1,2}/\d{1,2}$' THEN
            -- Handle YYYY/MM/DD format
            RETURN to_date(text_value, 'YYYY/MM/DD');
        ELSE
            -- Not a recognizable date format, return NULL
            RETURN NULL;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        -- If any parsing fails, return NULL
        RETURN NULL;
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION safe_to_date(TEXT) IS 'Safely converts text to date, returning NULL for invalid or non-date strings like "February-March" or "Before junior year"';


-- ============================================
-- Update the extract_goals_from_gameplan trigger function
-- ============================================
CREATE OR REPLACE FUNCTION extract_goals_from_gameplan()
RETURNS TRIGGER AS $$
DECLARE
  quick_win JSONB;
  long_term JSONB;
  plan JSONB;
BEGIN
  plan := NEW.plan_data;

  -- Extract quick wins as goals
  IF plan->'quickWins' IS NOT NULL THEN
    FOR quick_win IN SELECT * FROM jsonb_array_elements(plan->'quickWins')
    LOOP
      INSERT INTO student_items (
        user_id, item_type, item_subtype, title, description,
        tier1_state, metric_type, metric_value,
        source, confidence, extended_data
      ) VALUES (
        NEW.user_id,
        'goal',
        quick_win->>'category',
        quick_win->>'title',
        quick_win->>'description',
        'planned',
        'priority',
        quick_win->>'priority',
        'gameplan_extraction',
        'high',
        jsonb_build_object(
          'game_plan_id', NEW.id,
          'goal_type', 'quick_win',
          'time_commitment', quick_win->>'timeCommitment',
          'deadline_text', quick_win->>'deadline',  -- Store original text
          'impact', quick_win->'impact',
          'tips', quick_win->'tips',
          'extraction_date', NOW()
        )
      )
      ON CONFLICT DO NOTHING;
    END LOOP;
  END IF;

  -- Extract long term goals
  IF plan->'longTermGoals' IS NOT NULL THEN
    FOR long_term IN SELECT * FROM jsonb_array_elements(plan->'longTermGoals')
    LOOP
      INSERT INTO student_items (
        user_id, item_type, item_subtype, title, description,
        tier1_state, metric_type, metric_value, deadline_date,
        source, confidence, extended_data
      ) VALUES (
        NEW.user_id,
        'goal',
        long_term->>'category',
        long_term->>'title',
        long_term->>'description',
        'planned',
        'priority',
        long_term->>'priority',
        -- Use safe_to_date to avoid errors on non-date strings
        safe_to_date(long_term->>'deadline'),
        'gameplan_extraction',
        'high',
        jsonb_build_object(
          'game_plan_id', NEW.id,
          'goal_type', 'long_term',
          'time_commitment', long_term->>'timeCommitment',
          'deadline_text', long_term->>'deadline',  -- Store original text for display
          'impact', long_term->'impact',
          'tips', long_term->'tips',
          'extraction_date', NOW()
        )
      )
      ON CONFLICT DO NOTHING;
    END LOOP;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Note: The trigger itself doesn't need to be recreated since we're just
-- updating the function it calls

-- ============================================
-- Grant permissions
-- ============================================
GRANT EXECUTE ON FUNCTION safe_to_date(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION safe_to_date(TEXT) TO service_role;

-- ============================================
-- Verify
-- ============================================
DO $$
BEGIN
  -- Test the safe_to_date function
  ASSERT safe_to_date('2024-03-15') = '2024-03-15'::DATE, 'ISO date should parse';
  ASSERT safe_to_date('February-March for programs') IS NULL, 'Non-date should return NULL';
  ASSERT safe_to_date('Before junior year') IS NULL, 'Natural language should return NULL';
  ASSERT safe_to_date(NULL) IS NULL, 'NULL should return NULL';
  ASSERT safe_to_date('') IS NULL, 'Empty string should return NULL';
  RAISE NOTICE 'All safe_to_date tests passed!';
END;
$$;

SELECT 'Migration 041 complete: safe_to_date function created and trigger updated' AS status;
