import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import type { GamePlan, GamePlanPhase, GamePlanAction } from '@/lib/gamePlan/gamePlanEngine';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontSize: 11,
    fontFamily: 'Helvetica',
    backgroundColor: '#ffffff',
  },
  header: {
    marginBottom: 20,
    borderBottomWidth: 2,
    borderBottomColor: '#FF4A23',
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#641432',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  section: {
    marginTop: 20,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#641432',
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
    paddingBottom: 5,
  },
  summaryBox: {
    backgroundColor: '#fff5f3',
    padding: 15,
    borderRadius: 5,
    marginBottom: 15,
  },
  actionCard: {
    backgroundColor: '#f9fafb',
    padding: 12,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#FF4A23',
  },
  actionTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 5,
  },
  actionDescription: {
    fontSize: 10,
    color: '#4b5563',
    marginBottom: 5,
  },
  actionMeta: {
    fontSize: 9,
    color: '#6b7280',
  },
  bulletList: {
    marginLeft: 15,
    marginTop: 5,
  },
  bulletItem: {
    fontSize: 10,
    color: '#4b5563',
    marginBottom: 3,
  },
  priorityBadge: {
    fontSize: 8,
    color: '#ffffff',
    backgroundColor: '#FF4A23',
    padding: '2 6',
    borderRadius: 3,
    marginLeft: 8,
  },
  tipsSection: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  tipItem: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 2,
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 40,
    right: 40,
    textAlign: 'center',
    fontSize: 9,
    color: '#9ca3af',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    paddingTop: 10,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  strengthItem: {
    fontSize: 10,
    color: '#166534',
    marginBottom: 3,
  },
  gapItem: {
    fontSize: 10,
    color: '#9a3412',
    marginBottom: 3,
  },
  quickWinCard: {
    backgroundColor: '#fef2f2',
    padding: 10,
    marginBottom: 8,
    borderRadius: 4,
  },
  quickWinNumber: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#dc2626',
    marginRight: 8,
  },
  quickWinText: {
    fontSize: 11,
    color: '#374151',
  },
});

// ============================================================================
// INTERFACES
// ============================================================================

interface GamePlanPDFProps {
  gamePlan: GamePlan;
  studentName: string;
  studentGrade: number;
}

// ============================================================================
// COMPONENT
// ============================================================================

export const GamePlanPDF: React.FC<GamePlanPDFProps> = ({
  gamePlan,
  studentName,
  studentGrade,
}) => {
  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <Document>
      {/* Page 1: Overview */}
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{studentName}'s College Prep Game Plan</Text>
          <Text style={styles.subtitle}>
            {gamePlan.tierInfo.title} • Grade {studentGrade} • Generated {currentDate}
          </Text>
        </View>

        {/* Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Situation</Text>
          <View style={styles.summaryBox}>
            <Text style={{ fontSize: 11, color: '#374151', marginBottom: 8 }}>
              {gamePlan.tierInfo.description}
            </Text>
            <Text style={{ fontSize: 10, color: '#6b7280', fontStyle: 'italic' }}>
              {gamePlan.tierInfo.encouragement}
            </Text>
          </View>
        </View>

        {/* Strengths */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Strengths</Text>
          <View style={styles.bulletList}>
            {gamePlan.summary.strengthAreas.length > 0 ? (
              gamePlan.summary.strengthAreas.map((strength, index) => (
                <Text key={index} style={styles.strengthItem}>
                  ✓ {strength}
                </Text>
              ))
            ) : (
              <Text style={styles.bulletItem}>
                Starting fresh - building from a clean slate is an advantage!
              </Text>
            )}
          </View>
        </View>

        {/* Areas to Develop */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Areas to Develop</Text>
          <View style={styles.bulletList}>
            {gamePlan.summary.improvementAreas.map((area, index) => (
              <Text key={index} style={styles.gapItem}>
                → {area}
              </Text>
            ))}
          </View>
        </View>

        {/* Focus Recommendation */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Focus Area</Text>
          <View style={styles.summaryBox}>
            <Text style={{ fontSize: 11, color: '#374151' }}>
              {gamePlan.summary.focusRecommendation}
            </Text>
          </View>
        </View>

        {/* Quick Wins */}
        {gamePlan.quickWins.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Wins (Start This Week)</Text>
            {gamePlan.quickWins.slice(0, 3).map((action, index) => (
              <View key={action.id} style={styles.quickWinCard}>
                <View style={styles.row}>
                  <Text style={styles.quickWinNumber}>{index + 1}.</Text>
                  <Text style={styles.quickWinText}>{action.title}</Text>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Warnings */}
        {gamePlan.warnings.length > 0 && (
          <View style={styles.section}>
            <Text style={[styles.sectionTitle, { color: '#dc2626' }]}>Important Notes</Text>
            <View style={styles.bulletList}>
              {gamePlan.warnings.map((warning, index) => (
                <Text key={index} style={[styles.bulletItem, { color: '#dc2626' }]}>
                  ⚠ {warning}
                </Text>
              ))}
            </View>
          </View>
        )}

        <View style={styles.footer}>
          <Text>Generated by IvyQuest • Page 1</Text>
        </View>
      </Page>

      {/* Page 2+: Action Plans by Phase */}
      {gamePlan.phases.map((phase, phaseIndex) => (
        <Page key={phase.id} size="A4" style={styles.page}>
          <View style={styles.header}>
            <Text style={styles.title}>{phase.title}</Text>
            <Text style={styles.subtitle}>
              {phase.timeframe} • {phase.actions.length} actions
            </Text>
          </View>

          <Text style={{ fontSize: 11, color: '#6b7280', marginBottom: 16 }}>
            {phase.description}
          </Text>

          {phase.actions.map((action, actionIndex) => (
            <View key={action.id} style={styles.actionCard}>
              <View style={styles.row}>
                <Text style={styles.actionTitle}>
                  {actionIndex + 1}. {action.title}
                </Text>
                <Text
                  style={[
                    styles.priorityBadge,
                    {
                      backgroundColor:
                        action.priority === 'critical'
                          ? '#dc2626'
                          : action.priority === 'high'
                          ? '#FF4A23'
                          : action.priority === 'medium'
                          ? '#d97706'
                          : '#6b7280',
                    },
                  ]}
                >
                  {action.priority.toUpperCase()}
                </Text>
              </View>

              <Text style={styles.actionDescription}>{action.description}</Text>

              <Text style={styles.actionMeta}>
                ⏱ {action.timeCommitment}
                {action.deadline && ` • 📅 ${action.deadline}`}
                {` • +${action.impact.points} ${action.impact.pillar} points`}
              </Text>

              {/* Tips */}
              {action.tips.length > 0 && (
                <View style={styles.tipsSection}>
                  <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#374151', marginBottom: 4 }}>
                    Tips for Success:
                  </Text>
                  {action.tips.slice(0, 3).map((tip, tipIndex) => (
                    <Text key={tipIndex} style={styles.tipItem}>
                      • {tip}
                    </Text>
                  ))}
                </View>
              )}
            </View>
          ))}

          <View style={styles.footer}>
            <Text>
              Generated by IvyQuest • Page {phaseIndex + 2} • {currentDate}
            </Text>
          </View>
        </Page>
      ))}

      {/* Final Page: Long-Term Goals & Next Steps */}
      <Page size="A4" style={styles.page}>
        <View style={styles.header}>
          <Text style={styles.title}>Long-Term Goals & Next Steps</Text>
          <Text style={styles.subtitle}>Your path to college success</Text>
        </View>

        {/* Long-Term Goals */}
        {gamePlan.longTermGoals.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Major Milestones to Pursue</Text>
            {gamePlan.longTermGoals.slice(0, 5).map((goal, index) => (
              <View key={goal.id} style={styles.actionCard}>
                <Text style={styles.actionTitle}>
                  {goal.icon} {goal.title}
                </Text>
                <Text style={styles.actionDescription}>{goal.description}</Text>
                <Text style={styles.actionMeta}>
                  Category: {goal.category} • Impact: +{goal.impact.points} {goal.impact.pillar} points
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Weekly Commitment */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Commitment</Text>
          <View style={styles.summaryBox}>
            <Text style={{ fontSize: 14, fontWeight: 'bold', color: '#374151', marginBottom: 8 }}>
              Recommended Weekly Time: ~{gamePlan.weeklyCommitment} hours/week
            </Text>
            <Text style={{ fontSize: 10, color: '#6b7280' }}>
              This is based on your available time and the priority of each action.
              Quality matters more than quantity - focus on depth over breadth.
            </Text>
          </View>
        </View>

        {/* Next Steps */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Immediate Next Steps</Text>
          <View style={{ backgroundColor: '#f0fdf4', padding: 15, borderRadius: 5 }}>
            <Text style={{ fontSize: 11, color: '#166534', marginBottom: 8 }}>
              1. Review this game plan and identify your top 2-3 priorities
            </Text>
            <Text style={{ fontSize: 11, color: '#166534', marginBottom: 8 }}>
              2. Block time on your calendar for your first action this week
            </Text>
            <Text style={{ fontSize: 11, color: '#166534', marginBottom: 8 }}>
              3. Share this plan with a parent or counselor for accountability
            </Text>
            <Text style={{ fontSize: 11, color: '#166534' }}>
              4. Schedule a coaching call to discuss your personalized strategy
            </Text>
          </View>
        </View>

        {/* Contact */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Need Help?</Text>
          <Text style={{ fontSize: 10, color: '#6b7280' }}>
            Schedule a free consultation with an IvyQuest coach to review your game plan
            and get personalized guidance on your college prep journey.
          </Text>
        </View>

        <View style={styles.footer}>
          <Text>Generated by IvyQuest • Final Page • {currentDate}</Text>
        </View>
      </Page>
    </Document>
  );
};

export default GamePlanPDF;
