# IvyQuest v10.0 - Complete System Specification

## Document Information

| Field | Value |
|-------|-------|
| Version | 10.0.0 |
| Date | January 2026 |
| Status | Implementation Complete |
| Authors | Engineering Team |

---

# Part 1: Product Requirements Document (PRD)

## 1.1 Executive Summary

IvyQuest v10.0 is an AI-powered college admissions coaching platform that combines multiple specialized agents to deliver personalized, Jenny Duan-quality coaching at scale. The system transforms the traditionally expensive, high-touch college admissions consulting experience into an accessible, intelligent platform that guides students from profile assessment through application execution.

### Vision Statement

> "Democratize elite college admissions coaching by encoding Jenny Duan's proven methodology into an intelligent multi-agent system that delivers personalized guidance to every student."

### Key Value Propositions

1. **Personalization at Scale**: Each student receives a unique narrative and strategy based on their identity, aptitude, passion, and service
2. **Proactive Engagement**: System autonomously monitors progress and intervenes before students fall behind
3. **Expert-Quality Output**: Agent outputs match or exceed human coach quality (70%+ pass rate on Jenny Duan benchmark)
4. **Crisis Resilience**: Specialized protocol transforms setbacks into opportunities within 2 minutes

## 1.2 Problem Statement

### Current Pain Points

| Stakeholder | Pain Point | Impact |
|-------------|-----------|--------|
| Students | Generic advice doesn't fit their unique story | Weak applications, rejections |
| Students | Don't know when to start or what to prioritize | Missed deadlines, incomplete prep |
| Students | Setbacks derail motivation | Abandoned goals, anxiety |
| Parents | Premium coaching costs $10K-50K+ | Inequitable access |
| Coaches | Can only serve 20-30 students | Limited reach |

### Market Opportunity

- 3.7M+ US high school seniors annually
- <5% have access to premium coaching
- $7.7B college admissions market
- Growing demand for personalized guidance

## 1.3 Product Goals & Success Metrics

### Primary Goals

| Goal | Target | Measurement |
|------|--------|-------------|
| Narrative Quality | 70%+ pass rate | Evaluation Framework scores |
| Student Engagement | <72h avg response time | Activity tracking |
| Award Win Rate | >40% | Tracked outcomes |
| User Satisfaction | >4.5/5 rating | Post-session surveys |
| Execution Completion | >73% task completion | EDS monitoring |

### Key Performance Indicators (KPIs)

```
┌─────────────────────────────────────────────────────────────┐
│                    SUCCESS METRICS DASHBOARD                 │
├─────────────────────────────────────────────────────────────┤
│  Agent Quality        │  Student Outcomes    │  Engagement  │
│  ─────────────────    │  ─────────────────   │  ──────────  │
│  • Eval Pass Rate     │  • Award Wins        │  • DAU/MAU   │
│  • Jenny Alignment    │  • Acceptances       │  • Session   │
│  • Handoff Rate       │  • Profile Complete  │    Duration  │
│  • Response Time      │  • Tasks Completed   │  • Retention │
└─────────────────────────────────────────────────────────────┘
```

## 1.4 Scope & Features

### In Scope (v10.0)

| Feature | Priority | Status |
|---------|----------|--------|
| Assessment & Narrative Synthesis | P0 | Implemented |
| Awards Matching & Portfolio | P0 | Implemented |
| Opportunity Matching | P0 | Implemented |
| Game Plan Generation | P0 | Implemented |
| Execution Scaffolding | P0 | Implemented |
| Crisis Alchemy Protocol | P0 | Implemented |
| Proactive Workflows | P1 | Implemented |
| Evaluation Framework | P1 | Implemented |
| Notification System | P1 | Implemented |

### Out of Scope (Future)

- Essay writing assistance
- Interview preparation
- Financial aid optimization
- Parent portal
- Mobile native apps

## 1.5 User Personas

### Primary Persona: The Ambitious Student

```
┌────────────────────────────────────────────────────────────┐
│  PERSONA: Huda - The First-Gen STEM Changemaker            │
├────────────────────────────────────────────────────────────┤
│  Demographics:                                              │
│  • 16 years old, Grade 10                                  │
│  • South Asian, Muslim, Female                             │
│  • First-generation college student                        │
│  • Public school in suburban area                          │
│                                                            │
│  Goals:                                                    │
│  • Attend top CS/engineering program                       │
│  • Build apps that help underrepresented communities       │
│  • Stand out despite limited resources                     │
│                                                            │
│  Frustrations:                                             │
│  • Doesn't know where to start                            │
│  • Generic advice doesn't fit her story                   │
│  • Parents can't afford private coaches                   │
│  • Feels overwhelmed by competition                       │
│                                                            │
│  Behaviors:                                                │
│  • Highly motivated but needs direction                   │
│  • Active on weekday evenings                             │
│  • Responds well to specific, actionable guidance         │
└────────────────────────────────────────────────────────────┘
```

### Secondary Persona: The Coach

```
┌────────────────────────────────────────────────────────────┐
│  PERSONA: Sarah - The Overwhelmed Coach                    │
├────────────────────────────────────────────────────────────┤
│  Demographics:                                              │
│  • Former admissions officer                               │
│  • 5 years coaching experience                             │
│  • Managing 25 students                                    │
│                                                            │
│  Goals:                                                    │
│  • Help more students without sacrificing quality          │
│  • Identify at-risk students early                        │
│  • Focus time on high-value interventions                 │
│                                                            │
│  Frustrations:                                             │
│  • Can't scale personal attention                         │
│  • Misses early warning signs                             │
│  • Repetitive tasks consume creative time                 │
└────────────────────────────────────────────────────────────┘
```

---

# Part 2: Jobs-to-be-Done (JTBD) Framework

## 2.1 Core Jobs

### Job 1: Discover My Unique Story

```
┌────────────────────────────────────────────────────────────┐
│  JOB: When I'm starting my college journey, I want to      │
│       understand what makes me unique, so that I can       │
│       present a compelling, authentic narrative.           │
├────────────────────────────────────────────────────────────┤
│  FUNCTIONAL OUTCOMES:                                       │
│  • Minimize time to articulate my brand statement          │
│  • Increase confidence that my story is differentiated     │
│  • Minimize generic phrases that weaken my narrative       │
│                                                            │
│  EMOTIONAL OUTCOMES:                                        │
│  • Feel understood and validated                           │
│  • Feel confident about my direction                       │
│  • Feel excited rather than overwhelmed                    │
│                                                            │
│  SOCIAL OUTCOMES:                                          │
│  • Impress admissions officers                             │
│  • Stand out from similar applicants                       │
│  • Make parents proud of my progress                       │
├────────────────────────────────────────────────────────────┤
│  AGENT: NarrativeSynthesisAgent                            │
│  OUTPUT: Brand Statement, Narrative DNA, First Principle   │
└────────────────────────────────────────────────────────────┘
```

### Job 2: Build a Winning Portfolio

```
┌────────────────────────────────────────────────────────────┐
│  JOB: When I'm planning my activities, I want to know      │
│       which awards and opportunities will strengthen my    │
│       application, so that I invest time wisely.           │
├────────────────────────────────────────────────────────────┤
│  FUNCTIONAL OUTCOMES:                                       │
│  • Maximize probability of winning selected awards         │
│  • Minimize time spent on low-ROI opportunities            │
│  • Increase alignment between activities and narrative     │
│                                                            │
│  EMOTIONAL OUTCOMES:                                        │
│  • Feel strategic rather than scattered                    │
│  • Feel hopeful about achievable stretch goals             │
│  • Feel prepared with backup options                       │
├────────────────────────────────────────────────────────────┤
│  AGENTS: AwardsAgent, OpportunityAgent                     │
│  OUTPUT: Balanced portfolio (likely/target/stretch)        │
└────────────────────────────────────────────────────────────┘
```

### Job 3: Execute Without Overwhelm

```
┌────────────────────────────────────────────────────────────┐
│  JOB: When I have complex projects, I want clear next      │
│       steps I can complete today, so that I make           │
│       consistent progress without burning out.             │
├────────────────────────────────────────────────────────────┤
│  FUNCTIONAL OUTCOMES:                                       │
│  • Minimize task ambiguity                                 │
│  • Increase completion rate on daily goals                 │
│  • Minimize execution debt accumulation                    │
│                                                            │
│  EMOTIONAL OUTCOMES:                                        │
│  • Feel capable and in control                             │
│  • Feel momentum building                                  │
│  • Avoid paralysis from large goals                        │
├────────────────────────────────────────────────────────────┤
│  AGENT: ExecutionAgent                                     │
│  OUTPUT: Microsteps, Daily tasks, Progress tracking        │
└────────────────────────────────────────────────────────────┘
```

### Job 4: Recover from Setbacks

```
┌────────────────────────────────────────────────────────────┐
│  JOB: When I face rejection or failure, I want to          │
│       transform it into an opportunity, so that I          │
│       maintain motivation and improve my application.      │
├────────────────────────────────────────────────────────────┤
│  FUNCTIONAL OUTCOMES:                                       │
│  • Minimize time from crisis to productive action          │
│  • Increase quality of pivot activities                    │
│  • Minimize negative impact on application timeline        │
│                                                            │
│  EMOTIONAL OUTCOMES:                                        │
│  • Feel validated, not dismissed                           │
│  • Feel empowered with a concrete plan                     │
│  • Transform anxiety into determination                    │
├────────────────────────────────────────────────────────────┤
│  AGENT: ExecutionAgent (Crisis Alchemy)                    │
│  OUTPUT: Validation, Micro-action, Reframe, Pivot          │
└────────────────────────────────────────────────────────────┘
```

### Job 5: Stay on Track

```
┌────────────────────────────────────────────────────────────┐
│  JOB: When life gets busy, I want the system to keep       │
│       me accountable, so that I don't miss deadlines       │
│       or lose momentum.                                    │
├────────────────────────────────────────────────────────────┤
│  FUNCTIONAL OUTCOMES:                                       │
│  • Minimize missed deadlines                               │
│  • Increase awareness of upcoming milestones               │
│  • Minimize periods of disengagement                       │
│                                                            │
│  EMOTIONAL OUTCOMES:                                        │
│  • Feel supported, not nagged                              │
│  • Feel the system has my back                             │
│  • Feel celebrated for progress                            │
├────────────────────────────────────────────────────────────┤
│  WORKFLOWS: SilenceDetector, DeadlineAlerts,               │
│             WeeklyScout, DailyCheckin                      │
│  OUTPUT: Timely notifications, Escalations                 │
└────────────────────────────────────────────────────────────┘
```

## 2.2 Job Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STUDENT JOURNEY MAP                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DISCOVER          PLAN             EXECUTE          MONITOR             │
│  ────────          ────             ───────          ───────             │
│     │                │                 │                │                │
│     ▼                ▼                 ▼                ▼                │
│  ┌──────┐        ┌──────┐         ┌──────┐        ┌──────┐              │
│  │Assess│───────▶│Awards│────────▶│Scaff-│───────▶│Daily │              │
│  │ment  │        │Match │         │ old  │        │Check │              │
│  └──────┘        └──────┘         └──────┘        └──────┘              │
│     │                │                 │                │                │
│     ▼                ▼                 ▼                ▼                │
│  ┌──────┐        ┌──────┐         ┌──────┐        ┌──────┐              │
│  │Narr- │        │Oppor-│         │Crisis│        │Dead- │              │
│  │ative │        │tunity│         │Alch- │        │line  │              │
│  └──────┘        └──────┘         │emy   │        │Alert │              │
│     │                │            └──────┘        └──────┘              │
│     ▼                ▼                                  │                │
│  ┌──────┐        ┌──────┐                              ▼                │
│  │Game  │◀───────│Port- │                         ┌──────┐              │
│  │Plan  │        │folio │                         │Weekly│              │
│  └──────┘        └──────┘                         │Scout │              │
│                                                   └──────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.3 Outcome Prioritization Matrix

| Outcome | Importance | Satisfaction | Opportunity |
|---------|------------|--------------|-------------|
| Minimize time to articulate brand | 9 | 3 | 15 |
| Maximize award win probability | 9 | 4 | 14 |
| Minimize generic phrases | 8 | 3 | 13 |
| Minimize task ambiguity | 8 | 4 | 12 |
| Minimize missed deadlines | 9 | 5 | 13 |
| Transform setbacks quickly | 8 | 2 | 14 |

*Opportunity Score = Importance + (Importance - Satisfaction)*

---

# Part 3: UI/UX Specification

## 3.1 Information Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFORMATION ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  /                                                                       │
│  ├── /onboarding                                                        │
│  │   ├── /profile-setup        ← Identity, Demographics                 │
│  │   ├── /aptitude            ← GPA, Test Scores, APs                  │
│  │   ├── /passion             ← Activities, Leadership                  │
│  │   └── /service             ← Community Involvement                   │
│  │                                                                       │
│  ├── /dashboard                                                         │
│  │   ├── /overview            ← Narrative, Quick Stats                  │
│  │   ├── /opportunities       ← Tracked, Recommended                    │
│  │   ├── /awards              ← Portfolio, Win Tracking                 │
│  │   ├── /gameplan            ← Activities, Timeline                    │
│  │   └── /execution           ← Tasks, Projects, EDS                    │
│  │                                                                       │
│  ├── /profile                                                           │
│  │   ├── /narrative           ← Brand, DNA, Themes                      │
│  │   ├── /settings            ← Preferences, Notifications              │
│  │   └── /history             ← Activity Log                            │
│  │                                                                       │
│  └── /coach (role: coach)                                               │
│      ├── /students            ← Student List, Risk View                 │
│      ├── /tasks               ← Escalations, Handoffs                   │
│      └── /analytics           ← Performance, Trends                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Core Screen Specifications

### 3.2.1 Dashboard Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  IvyQuest                    🔔 3    👤 Huda                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  YOUR BRAND STATEMENT                                           │   │
│  │  ─────────────────────────────────────────────────────────────  │   │
│  │  "A South Asian Muslim innovator empowering girls through       │   │
│  │   code, building pathways to STEM equity in her community       │   │
│  │   and beyond."                                                  │   │
│  │                                                                 │   │
│  │  First Principle: BUILDER    Archetype: CHANGEMAKER             │   │
│  │  Confidence: 92%             [Regenerate] [Edit]                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  📊 TODAY'S TASKS │  │  🏆 AWARDS       │  │  🎯 OPPORTUNITIES│      │
│  │  ────────────────│  │  ────────────────│  │  ────────────────│      │
│  │  3 tasks due     │  │  5 tracking      │  │  8 matched       │      │
│  │  1 overdue       │  │  2 won           │  │  3 deadlines     │      │
│  │                  │  │                  │  │  this month      │      │
│  │  [View All →]    │  │  [View All →]    │  │  [View All →]    │      │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  UPCOMING DEADLINES                                              │   │
│  │  ─────────────────────────────────────────────────────────────  │   │
│  │  🔴 Jan 15  │ Regeneron STS        │ Application Due    │ 4 days │   │
│  │  🟡 Jan 22  │ NCWIT Award          │ Nomination Due     │ 11 days│   │
│  │  🟢 Feb 1   │ MIT THINK            │ Proposal Due       │ 21 days│   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2.2 Awards Portfolio View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AWARDS PORTFOLIO                                      [+ Add Award]    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Portfolio Balance                                                       │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  LIKELY (30%)     │████████░░░░░░░░░│ 3 awards                 │    │
│  │  TARGET (40%)     │██████████████░░░│ 4 awards                 │    │
│  │  STRETCH (30%)    │████████░░░░░░░░░│ 3 awards                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🟢 LIKELY WINS                                                  │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  Congressional App Challenge    │ 75% │ Nov 1  │ ⬤ Tracking    │   │
│  │  NCWIT Aspirations Award       │ 70% │ Jan 22 │ ⬤ Applying    │   │
│  │  Local STEM Fair               │ 85% │ Mar 15 │ ⬤ Tracking    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🟡 TARGET AWARDS                                                │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  Google Science Fair           │ 45% │ Feb 28 │ ⬤ Tracking    │   │
│  │  Scholastic Art & Writing      │ 50% │ Jan 5  │ ✓ Submitted   │   │
│  │  Davidson Fellows              │ 40% │ Feb 15 │ ⬤ Tracking    │   │
│  │  MIT THINK Scholars            │ 55% │ Feb 1  │ ⬤ Applying    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🔴 STRETCH GOALS                                                │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  Regeneron STS                 │ 15% │ Jan 15 │ ⬤ Applying    │   │
│  │  US Presidential Scholar       │ 10% │ Feb 1  │ ⬤ Tracking    │   │
│  │  Breakthrough Junior Challenge │ 20% │ Jun 15 │ ⬤ Tracking    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2.3 Crisis Alchemy Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CRISIS ALCHEMY                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  What happened?                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  I got rejected from the Google CSSI program. I worked so hard  │   │
│  │  on my application and now I feel like I'm not good enough...   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                        [Submit]         │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STEP 1: VALIDATE ✓                                        2 seconds    │
│  ─────────────────────────────────────────────────────────────────────  │
│  "That rejection stings, especially after all the effort you put in.   │
│   It's completely valid to feel disappointed and doubt yourself        │
│   right now."                                                          │
│                                                                          │
│  STEP 2: ACT ✓                                            10 seconds    │
│  ─────────────────────────────────────────────────────────────────────  │
│  "Right now, take 2 minutes to write down three specific things you    │
│   learned while preparing that application. Just bullet points."       │
│                                                                          │
│  [ ] I learned how to articulate my project's impact                   │
│  [ ] I practiced explaining technical concepts to non-technical        │
│  [ ] I identified gaps in my experience I can fill                     │
│                                                                          │
│  STEP 3: REFRAME ✓                                        30 seconds    │
│  ─────────────────────────────────────────────────────────────────────  │
│  "Here's the opportunity: CSSI accepts ~1,500 from 10,000+ applicants. │
│   The preparation you did isn't wasted—it's a foundation. And now you │
│   have free time this summer to create something even more impressive  │
│   that YOU control."                                                   │
│                                                                          │
│  STEP 4: CREATE                                            2 minutes    │
│  ─────────────────────────────────────────────────────────────────────  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  🚀 PIVOT ACTIVITY: "Code for Change Summer"                    │   │
│  │                                                                  │   │
│  │  Instead of attending CSSI, CREATE your own mini-program:       │   │
│  │                                                                  │   │
│  │  • Recruit 5 girls from your school who want to learn coding   │   │
│  │  • Run 4 Saturday workshops teaching app development           │   │
│  │  • Build a collaborative project together                      │   │
│  │  • Document with photos/video for your application             │   │
│  │                                                                  │   │
│  │  This transforms "rejected from program" into "founded a        │   │
│  │  program"—a much stronger story for MIT/Stanford.               │   │
│  │                                                                  │   │
│  │  [Accept & Start Planning]    [Modify]    [Talk to Coach]       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2.4 Notification Center

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NOTIFICATIONS                                    [Mark All Read]       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TODAY                                                                   │
│  ─────────────────────────────────────────────────────────────────────  │
│  🔴 URGENT  │ 1 day until Regeneron STS deadline!                       │
│     3:00 PM │ Submit your application now → [View]                      │
│                                                                          │
│  🟡 ALERT   │ NCWIT nomination requires teacher letter                  │
│     9:00 AM │ Request letter from Ms. Johnson today → [Action]          │
│                                                                          │
│  YESTERDAY                                                               │
│  ─────────────────────────────────────────────────────────────────────  │
│  🟢 SUCCESS │ Great progress! 5-day activity streak                     │
│     3:00 PM │ You're building momentum. Keep it up!                     │
│                                                                          │
│  ⚪ INFO    │ New opportunity matches your profile                      │
│     9:00 AM │ MIT PRIMES applications open → [Explore]                  │
│                                                                          │
│  THIS WEEK                                                               │
│  ─────────────────────────────────────────────────────────────────────  │
│  📋 DIGEST  │ Your weekly picks are here!                               │
│     Mon 9AM │ 3 opportunities + 2 awards matched → [View All]           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3.3 Design System

### Color Palette

```
┌─────────────────────────────────────────────────────────────────────────┐
│  BRAND COLORS                                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Primary                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                              │
│  │ #FF4A23  │  │ #641432  │  │ #FFFFFF  │                              │
│  │ Orange   │  │ Maroon   │  │ White    │                              │
│  │ Actions  │  │ Headings │  │ Backgrnd │                              │
│  └──────────┘  └──────────┘  └──────────┘                              │
│                                                                          │
│  Semantic                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ #16A34A  │  │ #D97706  │  │ #DC2626  │  │ #6B7280  │               │
│  │ Success  │  │ Warning  │  │ Error    │  │ Muted    │               │
│  │ Wins     │  │ Alerts   │  │ Urgent   │  │ Secondary│               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                          │
│  Deadline Tiers                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ 🟢 30d+  │  │ 🟡 7-30d │  │ 🟠 3-7d  │  │ 🔴 <3d   │               │
│  │ Low      │  │ Medium   │  │ High     │  │ Urgent   │               │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Typography

```
Font Family: Inter (UI), Georgia (Narrative text)

Headings:
  H1: 32px / Bold / Maroon (#641432)
  H2: 24px / Semibold / Gray-900
  H3: 18px / Medium / Gray-800

Body:
  Regular: 16px / Normal / Gray-700
  Small: 14px / Normal / Gray-600
  Caption: 12px / Normal / Gray-500

Brand Statement:
  24px / Georgia / Italic / Maroon
```

---

# Part 4: Technical Specification

## 4.1 System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                           ┌──────────────┐                              │
│                           │   Next.js    │                              │
│                           │   Frontend   │                              │
│                           └──────┬───────┘                              │
│                                  │                                       │
│                                  ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        API Gateway                                 │  │
│  │                    (FastAPI - Port 8001)                          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│          ┌───────────────────────┼───────────────────────┐              │
│          │                       │                       │              │
│          ▼                       ▼                       ▼              │
│  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐       │
│  │    AGENTS     │      │   WORKFLOWS   │      │  EVALUATION   │       │
│  │   (Reactive)  │      │  (Proactive)  │      │  (Quality)    │       │
│  └───────────────┘      └───────────────┘      └───────────────┘       │
│          │                       │                       │              │
│          └───────────────────────┼───────────────────────┘              │
│                                  │                                       │
│                                  ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         Supabase                                   │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │  │
│  │  │Profiles │  │ Awards  │  │Workflow │  │ Evalua- │              │  │
│  │  │         │  │ & Opps  │  │ State   │  │ tion    │              │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│                                  │                                       │
│                                  ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      External Services                             │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                           │  │
│  │  │ OpenAI  │  │ Claude  │  │  Email  │                           │  │
│  │  │  API    │  │   API   │  │ Service │                           │  │
│  │  └─────────┘  └─────────┘  └─────────┘                           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AGENT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     REACTIVE AGENTS                              │   │
│  │              (Respond to user requests)                          │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │   │
│  │  │  Assessment  │    │   Narrative  │    │   GamePlan   │      │   │
│  │  │    Agent     │───▶│  Synthesis   │───▶│    Agent     │      │   │
│  │  │              │    │    Agent     │    │              │      │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘      │   │
│  │         │                   │                   │               │   │
│  │         │                   │                   │               │   │
│  │         ▼                   ▼                   ▼               │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │   │
│  │  │    Awards    │    │  Opportunity │    │  Execution   │      │   │
│  │  │    Agent     │    │    Agent     │    │    Agent     │      │   │
│  │  │              │    │              │    │              │      │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘      │   │
│  │                                                  │               │   │
│  │                                                  ▼               │   │
│  │                                          ┌──────────────┐      │   │
│  │                                          │    Crisis    │      │   │
│  │                                          │   Alchemy    │      │   │
│  │                                          └──────────────┘      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    PROACTIVE WORKFLOWS                           │   │
│  │              (Run autonomously on schedule)                      │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │   │
│  │  │   Silence    │    │   Deadline   │    │   Weekly     │      │   │
│  │  │  Detector    │    │   Alerts     │    │   Scout      │      │   │
│  │  │  (4 hours)   │    │  (Daily 9AM) │    │ (Monday 9AM) │      │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘      │   │
│  │                                                                  │   │
│  │  ┌──────────────┐    ┌──────────────────────────────────┐      │   │
│  │  │    Daily     │    │         Workflow Runner          │      │   │
│  │  │   Checkin    │◀───│        (APScheduler)             │      │   │
│  │  │  (Daily 3PM) │    │                                  │      │   │
│  │  └──────────────┘    └──────────────────────────────────┘      │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.2 Agent Specifications

### Agent Inventory

| Agent | Purpose | Input | Output | LLM |
|-------|---------|-------|--------|-----|
| AssessmentAgent | Compute readiness metrics | Profile | CRI, Archetype | GPT-4o |
| NarrativeSynthesisAgent | Generate personal narrative | Profile | Brand, DNA, Themes | GPT-4o |
| GamePlanAgent | Create activity timeline | Profile + Narrative | Activities, Seeds | GPT-4o |
| AwardsAgent | Match and optimize awards | Profile + Narrative | Portfolio (L/T/S) | GPT-4o |
| OpportunityAgent | Match programs | Profile + Narrative | Recommendations | GPT-4o |
| ExecutionAgent | Scaffold projects | Project | Microsteps, EDS | GPT-4o |

### Agent Communication Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AGENT COMMUNICATION PATTERNS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PATTERN 1: Sequential Pipeline (Assessment Flow)                        │
│  ───────────────────────────────────────────────────────────────────    │
│                                                                          │
│      Profile    ┌────────────┐    Assessment   ┌────────────┐           │
│      Input  ───▶│ Assessment │───▶ Contract ───▶│ Narrative  │───▶ ...  │
│                 │   Agent    │                  │ Synthesis  │           │
│                 └────────────┘                  └────────────┘           │
│                                                                          │
│                                                                          │
│  PATTERN 2: Parallel Fan-Out (Matching)                                  │
│  ───────────────────────────────────────────────────────────────────    │
│                                                                          │
│                               ┌────────────┐                            │
│                           ┌──▶│   Awards   │──┐                         │
│                           │   │   Agent    │  │                         │
│      Narrative   ┌────────┴┐  └────────────┘  │  ┌────────────┐        │
│      DNA     ───▶│  Router │                  ├─▶│  Combine   │───▶    │
│                  └────────┬┘  ┌────────────┐  │  │  Results   │        │
│                           │   │Opportunity │  │  └────────────┘        │
│                           └──▶│   Agent    │──┘                         │
│                               └────────────┘                            │
│                                                                          │
│                                                                          │
│  PATTERN 3: Human-in-the-Loop (Crisis Alchemy)                          │
│  ───────────────────────────────────────────────────────────────────    │
│                                                                          │
│      Crisis    ┌────────────┐   Proposed   ┌────────────┐   Approved   │
│      Input ───▶│  Crisis    │───▶Response──▶│   HITL     │───▶Response │
│                │  Alchemy   │              │  Approval  │              │
│                └────────────┘              └────────────┘              │
│                                                   │                     │
│                                                   ▼                     │
│                                            ┌────────────┐              │
│                                            │   Coach    │              │
│                                            │   Queue    │              │
│                                            └────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.3 Data Flow Diagrams

### Assessment to Narrative Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│              DATA FLOW: Assessment → Narrative Synthesis                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        USER INPUT                                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Identity │ │ Aptitude │ │ Passion  │ │ Service  │           │   │
│  │  │ • Name   │ │ • GPA    │ │ • Spike  │ │ • Hours  │           │   │
│  │  │ • Grade  │ │ • SAT    │ │ • Leader │ │ • Impact │           │   │
│  │  │ • Demo   │ │ • APs    │ │ • Brag   │ │ • Level  │           │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │   │
│  └───────┼────────────┼────────────┼────────────┼──────────────────┘   │
│          │            │            │            │                       │
│          └────────────┴─────┬──────┴────────────┘                       │
│                             │                                            │
│                             ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    ASSESSMENT CONTRACT                           │   │
│  │  {                                                               │   │
│  │    "identity": {...},                                            │   │
│  │    "aptitude": { "academic_strength": 0.87, "ap_rigor": 0.92 }, │   │
│  │    "passion": { "spike_clarity": 0.85, "leadership_tier": 4 },  │   │
│  │    "service": { "depth_score": 0.78, "alignment": 0.91 }        │   │
│  │  }                                                               │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│                               ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 NARRATIVE SYNTHESIS AGENT                        │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │  Jenny's Formula:                                         │   │   │
│  │  │  IDENTITY + APTITUDE + PASSION + SERVICE = NARRATIVE      │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│                               ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    NARRATIVE OUTPUT                              │   │
│  │  {                                                               │   │
│  │    "brand_statement": "A South Asian Muslim innovator...",      │   │
│  │    "narrative_dna": "From her first line of code...",           │   │
│  │    "first_principle": "BUILDER",                                 │   │
│  │    "themes": ["STEM Equity", "Community", "Innovation"],        │   │
│  │    "archetype": { "id": "CHANGEMAKER", "confidence": 0.92 }     │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Workflow Execution Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│              DATA FLOW: Proactive Workflow Execution                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    WORKFLOW RUNNER                               │   │
│  │                   (APScheduler)                                  │   │
│  │  ┌────────────────────────────────────────────────────────┐     │   │
│  │  │  Cron Triggers:                                         │     │   │
│  │  │  • 0 */4 * * *  → SilenceDetector                      │     │   │
│  │  │  • 0 9 * * *    → DeadlineAlerts                       │     │   │
│  │  │  • 0 9 * * 1    → WeeklyScout                          │     │   │
│  │  │  • 0 15 * * *   → DailyCheckin                         │     │   │
│  │  └────────────────────────────────────────────────────────┘     │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│                               ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               SILENCE DETECTOR (Example)                         │   │
│  │                                                                  │   │
│  │  1. Query: profiles WHERE last_activity_at < NOW() - 72h        │   │
│  │                               │                                  │   │
│  │                               ▼                                  │   │
│  │  2. For each profile:                                           │   │
│  │     ┌────────────────────────────────────────────────────┐     │   │
│  │     │ • Check notification_preferences.silence_nudges    │     │   │
│  │     │ • Get workflow_state (nudge_count, last_nudge)     │     │   │
│  │     │ • Get profile_context (deadlines, incomplete)      │     │   │
│  │     │ • Select template (deadline/incomplete/general)    │     │   │
│  │     │ • Create notification                              │     │   │
│  │     │ • Update workflow_state                            │     │   │
│  │     └────────────────────────────────────────────────────┘     │   │
│  │                               │                                  │   │
│  │                               ▼                                  │   │
│  │  3. If nudge_count >= 3 AND days_inactive >= 7:                 │   │
│  │     → Escalate to coach_tasks                                   │   │
│  │                                                                  │   │
│  └────────────────────────────┬────────────────────────────────────┘   │
│                               │                                         │
│                               ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    WORKFLOW RESULT                               │   │
│  │  {                                                               │   │
│  │    "success": true,                                              │   │
│  │    "profiles_processed": 45,                                     │   │
│  │    "notifications_sent": 12,                                     │   │
│  │    "errors": [],                                                 │   │
│  │    "metadata": { "duration_ms": 2340 }                          │   │
│  │  }                                                               │   │
│  │           │                                                      │   │
│  │           ▼                                                      │   │
│  │    Stored in workflow_runs table                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.4 Message Sequence Diagrams

### Sequence 1: New Student Onboarding

```
┌─────────────────────────────────────────────────────────────────────────┐
│          SEQUENCE: New Student Assessment & Narrative                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Student    Frontend    API Gateway    Assessment    Narrative    DB    │
│     │          │            │              │            │          │    │
│     │  Submit  │            │              │            │          │    │
│     │  Profile │            │              │            │          │    │
│     │─────────▶│            │              │            │          │    │
│     │          │            │              │            │          │    │
│     │          │  POST /profile            │            │          │    │
│     │          │───────────▶│              │            │          │    │
│     │          │            │              │            │          │    │
│     │          │            │  Store Profile            │          │    │
│     │          │            │──────────────────────────────────────▶│    │
│     │          │            │              │            │          │    │
│     │          │            │  profile_id  │            │          │    │
│     │          │            │◀──────────────────────────────────────│    │
│     │          │            │              │            │          │    │
│     │          │  POST /agents/assessment/enhance       │          │    │
│     │          │───────────▶│              │            │          │    │
│     │          │            │              │            │          │    │
│     │          │            │  enhance()   │            │          │    │
│     │          │            │─────────────▶│            │          │    │
│     │          │            │              │            │          │    │
│     │          │            │              │  Compute   │          │    │
│     │          │            │              │  CRI, Arch │          │    │
│     │          │            │              │────────────│          │    │
│     │          │            │              │            │          │    │
│     │          │            │  AssessmentContract       │          │    │
│     │          │            │◀─────────────│            │          │    │
│     │          │            │              │            │          │    │
│     │          │  POST /agents/narrative/synthesize     │          │    │
│     │          │───────────▶│              │            │          │    │
│     │          │            │              │            │          │    │
│     │          │            │  synthesize()│            │          │    │
│     │          │            │─────────────────────────▶│          │    │
│     │          │            │              │            │          │    │
│     │          │            │              │   GPT-4o   │          │    │
│     │          │            │              │   Call     │          │    │
│     │          │            │              │   ────────▶│          │    │
│     │          │            │              │            │          │    │
│     │          │            │              │  Brand +   │          │    │
│     │          │            │              │  DNA +     │          │    │
│     │          │            │              │  Themes    │          │    │
│     │          │            │◀──────────────────────────│          │    │
│     │          │            │              │            │          │    │
│     │          │            │  Store Narrative          │          │    │
│     │          │            │──────────────────────────────────────▶│    │
│     │          │            │              │            │          │    │
│     │          │  NarrativeResult          │            │          │    │
│     │          │◀───────────│              │            │          │    │
│     │          │            │              │            │          │    │
│     │  Display │            │              │            │          │    │
│     │  Result  │            │              │            │          │    │
│     │◀─────────│            │              │            │          │    │
│     │          │            │              │            │          │    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sequence 2: Crisis Alchemy Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│          SEQUENCE: Crisis Alchemy with HITL Approval                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Student    Frontend    API       Execution    LangGraph    Coach   DB  │
│     │          │         │            │            │          │      │  │
│     │  Report  │         │            │            │          │      │  │
│     │  Crisis  │         │            │            │          │      │  │
│     │─────────▶│         │            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │  POST /agents/execution/crisis        │      │      │  │
│     │          │────────▶│            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │  handle_crisis()           │          │      │  │
│     │          │         │───────────▶│            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │  Execute   │          │      │  │
│     │          │         │            │  4-Step    │          │      │  │
│     │          │         │            │  Protocol  │          │      │  │
│     │          │         │            │───────────▶│          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │  Step 1: Validate     │      │  │
│     │          │         │            │  Step 2: Act          │      │  │
│     │          │         │            │  Step 3: Reframe      │      │  │
│     │          │         │            │  Step 4: Create       │      │  │
│     │          │         │            │◀───────────│          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │  Create HITL Request   │      │  │
│     │          │         │            │──────────────────────────────▶│  │
│     │          │         │            │            │          │      │  │
│     │          │         │  Proposed Response       │          │      │  │
│     │          │         │  (status: pending)       │          │      │  │
│     │          │◀────────│            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │  Show    │         │            │            │          │      │  │
│     │  Pending │         │            │            │          │      │  │
│     │◀─────────│         │            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │   [Async]  │  Notify  │      │  │
│     │          │         │            │────────────────────────▶      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │            │  Review  │      │  │
│     │          │         │            │            │  ────────│      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │  POST /agents/handoff/approve      │      │  │
│     │          │         │◀────────────────────────────────────      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │  Approve Response        │          │      │  │
│     │          │         │───────────▶│            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │          │         │            │  Update Status        │      │  │
│     │          │         │            │──────────────────────────────▶│  │
│     │          │         │            │            │          │      │  │
│     │          │  WebSocket: Response Approved      │          │      │  │
│     │          │◀────────│            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│     │  Display │         │            │            │          │      │  │
│     │  Final   │         │            │            │          │      │  │
│     │  Response│         │            │            │          │      │  │
│     │◀─────────│         │            │            │          │      │  │
│     │          │         │            │            │          │      │  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sequence 3: Proactive Workflow Execution

```
┌─────────────────────────────────────────────────────────────────────────┐
│          SEQUENCE: Deadline Alert Workflow                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  APScheduler    Runner    DeadlineAlert    DB    Notification    User   │
│       │            │            │           │          │           │    │
│       │  Cron      │            │           │          │           │    │
│       │  Trigger   │            │           │          │           │    │
│       │  0 9 * * * │            │           │          │           │    │
│       │───────────▶│            │           │          │           │    │
│       │            │            │           │          │           │    │
│       │            │  run()     │           │          │           │    │
│       │            │───────────▶│           │          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  Query    │          │           │    │
│       │            │            │  Profiles │          │           │    │
│       │            │            │──────────▶│          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  [profile_ids]       │           │    │
│       │            │            │◀──────────│          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  For each profile:   │           │    │
│       │            │            │  ─────────────────── │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  Query    │          │           │    │
│       │            │            │  student_ │          │           │    │
│       │            │            │  opps +   │          │           │    │
│       │            │            │  awards   │          │           │    │
│       │            │            │──────────▶│          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  [items with deadlines]          │    │
│       │            │            │◀──────────│          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  Check days_until    │           │    │
│       │            │            │  Match tier (30/7/3/1)           │    │
│       │            │            │  ─────────────────── │           │    │
│       │            │            │           │          │           │    │
│       │            │            │  If match & not already sent:    │    │
│       │            │            │           │          │           │    │
│       │            │            │  Create   │          │           │    │
│       │            │            │  Notif    │          │           │    │
│       │            │            │──────────▶│          │           │    │
│       │            │            │           │          │           │    │
│       │            │            │           │  Insert  │           │    │
│       │            │            │           │  notif   │           │    │
│       │            │            │           │─────────▶│           │    │
│       │            │            │           │          │           │    │
│       │            │            │           │          │  Push     │    │
│       │            │            │           │          │  Notif    │    │
│       │            │            │           │          │──────────▶│    │
│       │            │            │           │          │           │    │
│       │            │            │  Update   │          │           │    │
│       │            │            │  workflow_│          │           │    │
│       │            │            │  state    │          │           │    │
│       │            │            │──────────▶│          │           │    │
│       │            │            │           │          │           │    │
│       │            │  WorkflowResult        │          │           │    │
│       │            │◀───────────│           │          │           │    │
│       │            │            │           │          │           │    │
│       │            │  Log to    │           │          │           │    │
│       │            │  workflow_ │           │          │           │    │
│       │            │  runs      │           │          │           │    │
│       │            │────────────────────────▶          │           │    │
│       │            │            │           │          │           │    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sequence 4: Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│          SEQUENCE: Agent Evaluation Run                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Admin    API    Pipeline    Golden    ObjectiveCalc    LLMJudge    DB  │
│    │       │         │         │            │              │         │  │
│    │  POST │         │         │            │              │         │  │
│    │  /eval/run/narrative      │            │              │         │  │
│    │──────▶│         │         │            │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │  run_full_evaluation()         │              │         │  │
│    │       │────────▶│         │            │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  load_all()          │              │         │  │
│    │       │         │────────▶│            │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  [GoldenExamples]    │              │         │  │
│    │       │         │◀────────│            │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  For each golden:    │              │         │  │
│    │       │         │  ────────────────    │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  Call NarrativeAgent │              │         │  │
│    │       │         │  with input_profile  │              │         │  │
│    │       │         │  ────────────────    │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  agent_output        │              │         │  │
│    │       │         │  ────────────────    │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  calculate_narrative_metrics()     │         │  │
│    │       │         │───────────────────────▶            │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │         │  identity_coverage       │         │  │
│    │       │         │         │  theme_alignment         │         │  │
│    │       │         │         │  forbidden_absence       │         │  │
│    │       │         │         │  specificity_score       │         │  │
│    │       │         │◀──────────────────────│            │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  evaluate_narrative() │              │         │  │
│    │       │         │──────────────────────────────────────▶        │  │
│    │       │         │         │            │              │         │  │
│    │       │         │         │            │   GPT-4o    │         │  │
│    │       │         │         │            │   Rubric    │         │  │
│    │       │         │         │            │   ─────────▶│         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │         │  authenticity: 4         │         │  │
│    │       │         │         │  identity_integration: 5 │         │  │
│    │       │         │         │  narrative_power: 4      │         │  │
│    │       │         │         │  jenny_alignment: 4      │         │  │
│    │       │         │         │  actionability: 5        │         │  │
│    │       │         │◀─────────────────────────────────────        │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  Combine Scores:     │              │         │  │
│    │       │         │  obj_avg * 0.4 + subj_avg * 0.6   │         │  │
│    │       │         │  ─────────────────── │              │         │  │
│    │       │         │         │            │              │         │  │
│    │       │         │  Store Result        │              │         │  │
│    │       │         │──────────────────────────────────────────────▶│  │
│    │       │         │         │            │              │         │  │
│    │       │  Aggregate Results │            │              │         │  │
│    │       │  (pass_rate, avg_score, weaknesses)          │         │  │
│    │       │◀────────│         │            │              │         │  │
│    │       │         │         │            │              │         │  │
│    │  Results        │         │            │              │         │  │
│    │◀──────│         │         │            │              │         │  │
│    │       │         │         │            │              │         │  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.5 Database Schema

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATABASE ENTITY RELATIONSHIPS                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐       ┌─────────────────┐                          │
│  │    profiles     │       │     awards      │                          │
│  ├─────────────────┤       ├─────────────────┤                          │
│  │ id (PK)         │       │ id (PK)         │                          │
│  │ email           │       │ name            │                          │
│  │ first_name      │       │ category        │                          │
│  │ grade           │       │ level           │                          │
│  │ role            │       │ deadline        │                          │
│  │ narrative_*     │       │ prestige_score  │                          │
│  │ last_activity_at│       │ eligibility     │                          │
│  └────────┬────────┘       └────────┬────────┘                          │
│           │                         │                                    │
│           │  1                      │  1                                 │
│           │                         │                                    │
│           │  ┌──────────────────────┼──────────────────────┐            │
│           │  │                      │                      │            │
│           ▼  ▼                      ▼                      ▼            │
│  ┌─────────────────┐       ┌─────────────────┐    ┌─────────────────┐  │
│  │ student_awards  │       │student_opportun-│    │  notifications  │  │
│  ├─────────────────┤       │     ities       │    ├─────────────────┤  │
│  │ id (PK)         │       ├─────────────────┤    │ id (PK)         │  │
│  │ profile_id (FK) │       │ id (PK)         │    │ profile_id (FK) │  │
│  │ award_id (FK)   │       │ profile_id (FK) │    │ title           │  │
│  │ status          │       │ opportunity_id  │    │ message         │  │
│  │ win_probability │       │ status          │    │ type            │  │
│  └─────────────────┘       │ fit_score       │    │ read            │  │
│           │                └─────────────────┘    │ source_workflow │  │
│           │  *                      │  *          └─────────────────┘  │
│           │                         │                      │  *         │
│           │                         │                      │            │
│           ▼                         ▼                      │            │
│  ┌─────────────────┐       ┌─────────────────┐            │            │
│  │  opportunities  │       │  workflow_state │◀───────────┘            │
│  ├─────────────────┤       ├─────────────────┤                          │
│  │ id (PK)         │       │ id (PK)         │                          │
│  │ name            │       │ profile_id (FK) │                          │
│  │ type            │       │ workflow_name   │                          │
│  │ category        │       │ last_run        │                          │
│  │ deadline        │       │ state (JSONB)   │                          │
│  │ prestige_score  │       │ enabled         │                          │
│  └─────────────────┘       └─────────────────┘                          │
│                                     │                                    │
│                                     │  *                                 │
│                                     ▼                                    │
│                            ┌─────────────────┐                          │
│                            │  workflow_runs  │                          │
│                            ├─────────────────┤                          │
│                            │ id (PK)         │                          │
│                            │ workflow_name   │                          │
│                            │ success         │                          │
│                            │ profiles_proc.  │                          │
│                            │ notifications   │                          │
│                            │ duration_ms     │                          │
│                            └─────────────────┘                          │
│                                                                          │
│  ┌─────────────────┐       ┌─────────────────┐                          │
│  │evaluation_golden│       │ evaluation_runs │                          │
│  ├─────────────────┤       ├─────────────────┤                          │
│  │ id (PK)         │───────│ golden_id (FK)  │                          │
│  │ profile_id      │   1:* │ id (PK)         │                          │
│  │ input_profile   │       │ run_id          │                          │
│  │ expected_outputs│       │ agent_version   │                          │
│  │ jenny_annotate  │       │ objective_scores│                          │
│  │ difficulty_tier │       │ llm_judge_scores│                          │
│  │ tags            │       │ overall_score   │                          │
│  └─────────────────┘       │ passed          │                          │
│                            └─────────────────┘                          │
│                                                                          │
│  ┌─────────────────┐                                                    │
│  │  coach_tasks    │                                                    │
│  ├─────────────────┤                                                    │
│  │ id (PK)         │                                                    │
│  │ profile_id (FK) │                                                    │
│  │ coach_id (FK)   │                                                    │
│  │ task_type       │                                                    │
│  │ priority        │                                                    │
│  │ status          │                                                    │
│  │ resolution      │                                                    │
│  └─────────────────┘                                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 4.6 API Specification

### API Endpoint Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         API ENDPOINTS                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  HEALTH & STATUS                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET  /                           Root info                             │
│  GET  /health                     Health check                          │
│                                                                          │
│  ASSESSMENT AGENTS                                                       │
│  ─────────────────────────────────────────────────────────────────────  │
│  POST /agents/assessment/enhance  Run full assessment                   │
│  POST /agents/narrative/synthesize Generate narrative                   │
│  GET  /agents/narrative/{id}      Get existing narrative                │
│                                                                          │
│  EXECUTION AGENTS                                                        │
│  ─────────────────────────────────────────────────────────────────────  │
│  POST /agents/execution/scaffold  Break project into steps              │
│  POST /agents/execution/crisis    Crisis Alchemy protocol               │
│  POST /agents/handoff/approve     HITL approval                         │
│  GET  /agents/execution/blockers/{id}  Detect blocked projects          │
│  GET  /agents/execution/eds/{id}  Get Execution Debt Score              │
│                                                                          │
│  MATCHING AGENTS                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│  POST /agents/gameplan/generate   Generate game plan                    │
│  GET  /agents/awards/match/{id}   Match awards                          │
│  GET  /agents/opportunities/match/{id}  Match opportunities             │
│                                                                          │
│  NOTIFICATIONS                                                           │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET  /notifications/{id}         Get notifications                     │
│  POST /notifications/mark-read    Mark as read                          │
│  POST /notifications/{id}/mark-all-read  Mark all read                  │
│  GET  /notifications/{id}/count   Get unread count                      │
│                                                                          │
│  WORKFLOWS                                                               │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET  /workflows/status           Scheduler status                      │
│  POST /workflows/run              Run single workflow                   │
│  POST /workflows/run-all          Run all workflows                     │
│  POST /workflows/pause            Pause workflow                        │
│  POST /workflows/resume           Resume workflow                       │
│  GET  /workflows/runs             Get run history                       │
│  GET  /workflows/deadlines/{id}   Get deadlines                         │
│                                                                          │
│  EVALUATION                                                              │
│  ─────────────────────────────────────────────────────────────────────  │
│  GET  /evaluation/golden          List golden examples                  │
│  GET  /evaluation/golden/{id}     Get golden example                    │
│  GET  /evaluation/golden-stats    Dataset statistics                    │
│  POST /evaluation/run/{agent}     Run evaluation                        │
│  GET  /evaluation/runs            Get eval history                      │
│  GET  /evaluation/runs/{id}       Get run details                       │
│  GET  /evaluation/trends          Score trends                          │
│  GET  /evaluation/compare         Compare versions                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sample API Contracts

#### POST /agents/narrative/synthesize

**Request:**
```json
{
  "profile_id": "uuid-string",
  "assessment_contract": {
    "identity": {
      "firstName": "Huda",
      "grade": 10,
      "culturalBackground": ["SOUTH_ASIAN"],
      "gender": "FEMALE",
      "religion": "Muslim",
      "firstGeneration": true
    },
    "aptitude": {
      "gpa_weighted": 3.9,
      "sat_total": 1570,
      "ap_count": 8,
      "academic_strength": 0.87
    },
    "passion": {
      "spike_category": "STEM",
      "leadership_level": "FOUNDER_LOCAL",
      "spike_clarity": 0.85
    },
    "service": {
      "hours": 350,
      "depth_score": 0.78
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "brand_statement": "A South Asian Muslim innovator empowering girls through code, building pathways to STEM equity in her community and beyond.",
  "narrative_dna": "From her first line of code in seventh grade to founding CodeGirls Academy, Huda has transformed her passion for technology into a mission...",
  "first_principle": "BUILDER",
  "themes": [
    "STEM Equity",
    "Community Empowerment",
    "Cultural Bridge-Building",
    "First-Generation Success",
    "Impact through Innovation"
  ],
  "archetype": {
    "id": "CHANGEMAKER",
    "label": "Impact-Driven Innovator",
    "confidence": 0.92
  },
  "confidence": 0.89,
  "handoff_recommended": false
}
```

#### POST /agents/execution/crisis

**Request:**
```json
{
  "profile_id": "uuid-string",
  "crisis_type": "rejection",
  "description": "I got rejected from Google CSSI. I worked so hard on my application and now I feel like I'm not good enough.",
  "urgency": 4
}
```

**Response:**
```json
{
  "success": true,
  "status": "pending_approval",
  "crisis_id": "crisis-uuid",
  "response": {
    "validation": "That rejection stings, especially after all the effort you put in. It's completely valid to feel disappointed and doubt yourself right now.",
    "micro_action": "Right now, take 2 minutes to write down three specific things you learned while preparing that application. Just bullet points.",
    "reframe": "Here's the opportunity: CSSI accepts ~1,500 from 10,000+ applicants. The preparation you did isn't wasted—it's a foundation. And now you have free time this summer to create something even more impressive that YOU control.",
    "pivot_activity": {
      "name": "Code for Change Summer",
      "description": "Create your own coding program for underrepresented girls",
      "steps": [
        "Recruit 5 girls from your school",
        "Design 4 Saturday workshops",
        "Build a collaborative project",
        "Document with photos/video"
      ],
      "impact": "Transforms 'rejected from program' into 'founded a program'"
    }
  },
  "requires_coach_approval": true,
  "approval_deadline": "2026-01-12T15:00:00Z"
}
```

---

# Part 5: Implementation Summary

## 5.1 Component Inventory

### Agents (6 Reactive)

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| AssessmentAgent | `agents/assessment.py` | ~200 | Implemented |
| NarrativeSynthesisAgent | `agents/narrative_synthesis.py` | ~300 | Implemented |
| GamePlanAgent | `agents/gameplan.py` | ~250 | Implemented |
| AwardsAgent | `agents/awards.py` | ~280 | Implemented |
| OpportunityAgent | `agents/opportunity.py` | ~260 | Implemented |
| ExecutionAgent | `agents/execution.py` | ~350 | Implemented |

### Workflows (4 Proactive)

| Component | File | Lines | Schedule |
|-----------|------|-------|----------|
| SilenceDetector | `workflows/silence_detector.py` | 250 | Every 4h |
| DeadlineAlerts | `workflows/deadline_alerts.py` | 340 | Daily 9AM |
| WeeklyScout | `workflows/weekly_scout.py` | 340 | Monday 9AM |
| DailyCheckin | `workflows/daily_checkin.py` | 320 | Daily 3PM |
| WorkflowRunner | `workflows/runner.py` | 260 | - |
| BaseWorkflow | `workflows/base.py` | 321 | - |

### Evaluation Framework

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| GoldenDatasetLoader | `evaluation/golden_loader.py` | 170 | Load benchmarks |
| ObjectiveMetricsCalculator | `evaluation/objective_metrics.py` | 380 | Automated checks |
| LLMJudge | `evaluation/llm_judge.py` | 340 | GPT-4 scoring |
| EvaluationPipeline | `evaluation/pipeline.py` | 350 | Orchestration |
| Narrative Rubric | `evaluation/rubrics/narrative.py` | 175 | - |
| Awards Rubric | `evaluation/rubrics/awards.py` | 165 | - |
| Crisis Rubric | `evaluation/rubrics/crisis.py` | 190 | - |

### Database

| Migration | File | Tables Created |
|-----------|------|----------------|
| 007 | `007_opportunities_awards.sql` | awards, opportunities, student_applications |
| 020 | `020_evaluation_and_workflows.sql` | evaluation_golden, evaluation_runs, workflow_state, notifications, coach_tasks |
| 021 | `021_workflow_runs.sql` | workflow_runs |

### Seed Data

| Dataset | Count | File |
|---------|-------|------|
| Awards | 97 | `seeds/awards_data.py` |
| Opportunities | 58 | `seeds/opportunities_data.py` |
| Golden Examples | 3 | `scripts/seed_database.py` |

## 5.2 Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TECHNOLOGY STACK                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  FRONTEND                      │  BACKEND                               │
│  ─────────────────────────────│─────────────────────────────────       │
│  • Next.js 14                  │  • FastAPI                             │
│  • React 18                    │  • Python 3.11+                        │
│  • TypeScript                  │  • Pydantic v2                         │
│  • Tailwind CSS                │  • APScheduler                         │
│  • Zustand (state)             │  • Structlog                           │
│                                │                                         │
│  DATABASE                      │  AI/ML                                  │
│  ─────────────────────────────│─────────────────────────────────       │
│  • Supabase (PostgreSQL)       │  • OpenAI GPT-4o                       │
│  • Row Level Security          │  • LangChain/LangGraph                 │
│  • Real-time subscriptions     │  • Agno Framework                      │
│                                │                                         │
│  INFRASTRUCTURE                │  MONITORING                            │
│  ─────────────────────────────│─────────────────────────────────       │
│  • Docker                      │  • Structlog (JSON logs)               │
│  • Vercel (frontend)           │  • Workflow run tracking               │
│  • Railway/Render (backend)    │  • Evaluation trends                   │
│                                │                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 5.3 Quality Assurance

### Evaluation Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Narrative Pass Rate | 70%+ | Evaluation Framework |
| Jenny Alignment | 4+ / 5 | LLM Judge |
| Identity Coverage | 80%+ | Objective Metrics |
| Forbidden Phrases | 0 | Objective Metrics |
| Award Win Rate | 40%+ | Outcome Tracking |

### Testing Strategy

1. **Unit Tests**: Individual agent functions
2. **Integration Tests**: API endpoint behavior
3. **Golden Dataset Tests**: Benchmark against Jenny's examples
4. **Regression Tests**: Version comparison via evaluation

---

# Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Brand Statement** | One-sentence (15-25 words) summary of student's unique value proposition |
| **CRI** | College Readiness Index - composite score of application strength |
| **Crisis Alchemy** | 4-step protocol (Validate→Act→Reframe→Create) for handling setbacks |
| **EDS** | Execution Debt Score - measure of incomplete tasks (target: <50) |
| **First Principle** | Core motivation type (BUILDER, STORYTELLER, DISCOVERER, ADVOCATE, CONNECTOR, HEALER, LEADER) |
| **Golden Example** | Benchmark case from Jenny Duan's actual coaching |
| **HITL** | Human-In-The-Loop - coach approval for sensitive responses |
| **Narrative DNA** | Extended 2-3 paragraph personalized story |
| **Spike** | Primary area of focused excellence |
| **Strategic Overwhelm** | Assigning 1.4x tasks expecting 73% completion |

---

# Appendix B: File Structure

```
agents/
├── agents/
│   ├── __init__.py
│   ├── assessment.py
│   ├── awards.py
│   ├── execution.py
│   ├── gameplan.py
│   ├── narrative_synthesis.py
│   └── opportunity.py
├── evaluation/
│   ├── __init__.py
│   ├── golden_loader.py
│   ├── llm_judge.py
│   ├── objective_metrics.py
│   ├── pipeline.py
│   └── rubrics/
│       ├── __init__.py
│       ├── awards.py
│       ├── crisis.py
│       └── narrative.py
├── workflows/
│   ├── __init__.py
│   ├── base.py
│   ├── daily_checkin.py
│   ├── deadline_alerts.py
│   ├── runner.py
│   ├── silence_detector.py
│   └── weekly_scout.py
├── seeds/
│   ├── awards_data.py
│   └── opportunities_data.py
├── scripts/
│   └── seed_database.py
├── tools/
│   └── database.py
├── config.py
├── main.py
└── requirements.txt

supabase/migrations/
├── 007_opportunities_awards.sql
├── 020_evaluation_and_workflows.sql
└── 021_workflow_runs.sql
```

---

*Document Version: 1.0.0*
*Last Updated: January 2026*
*Total System Lines of Code: ~6,500+*
