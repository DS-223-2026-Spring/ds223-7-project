# Problem

## Context

**Armat** is an Armenian writing and document-export SaaS platform operating on a freemium model. It has 4,420 active free-tier users ("writers") who can create documents and export them — but hit export and feature limits on the free plan. Converting these users to the paid **Pro** plan (AMD 2,900/month) is the core business challenge.

## Problem Statement

Armat has no systematic, data-driven way to identify which free users are most likely to convert and to reach them with the right message at the right time. All free users are treated identically, so conversion campaigns are generic and ineffective.

## Root Causes

- **No segmentation** — users with very different engagement levels (heavy exporters vs. inactive) receive the same messaging
- **No campaign tooling** — PMs have no internal interface to write, launch, or test targeted conversion messages
- **No A/B testing** — no way to learn which message variant converts best for each user type
- **No conversion analytics** — no real-time dashboard to track what is working

## Current State (Milestone 1 Baseline)

| Metric | Value |
|--------|-------|
| Total free users | 4,420 |
| Conversion rate | 5.4% (+2.1 pp vs baseline) |
| Avg time to convert | 6.2 days (−3.8 days vs control) |
| 30-day Pro retention | 83% (target: 80% ✓) |

## User Segments (from Milestone 1 analysis)

| Segment | Count | Description |
|---------|-------|-------------|
| Power writers | 1,240 | High-frequency exporters who regularly hit limits |
| Growing writers | 1,580 | Increasing usage trend, not yet limit-bound |
| Casual writers | 980 | Occasional use, interested in template library |
| Dormant writers | 620 | Inactive — need a win-back offer |

## Solution: Pulse

**Pulse** is a free-to-paid conversion platform built for Armat's PM team that:

1. Segments users into the four behavioural groups above
2. Lets PMs craft and send targeted in-app messages per segment (e.g. *"You've exported 9 times and hit limits 7 times — go unlimited for AMD 2,900/month"*)
3. Runs 14-day A/B tests on message variants to measure conversion lift
4. Tracks all KPIs in a live dashboard with per-segment funnel breakdowns