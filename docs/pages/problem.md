# Problem & Solution

## Context

**Mer Lezun** is an Armenian writing and document-export SaaS platform operating on a freemium model. Free-tier users can create documents and export them but hit feature and export limits on the free plan. Converting these users to the paid **Pro** plan (AMD 2,900/month) is the core business challenge.

## Problem Statement

Mer Lezun had no systematic, data-driven way to identify which free users are most likely to convert, or to reach them with the right message at the right time. All free users were treated identically — conversion campaigns were generic and ineffective.

## Root Causes

- **No segmentation** — users with very different engagement levels received the same messaging
- **No campaign tooling** — PMs had no internal interface to write, launch, or test targeted messages
- **No A/B testing** — no way to learn which message variant converts best per user type
- **No conversion analytics** — no real-time dashboard to track what is working

## User Segments

Behavioral clustering on session activity, export frequency, and paywall interactions produced four segments:

| Segment | Count | Description |
|---------|-------|-------------|
| Power users | 66 | High-frequency exporters who regularly hit limits |
| Growing users | 110 | Increasing usage trend, approaching limits |
| Casual users | 155 | Occasional use, interested in template library |
| Dormant users | 111 | Inactive — need a win-back offer |

## Solution: Pulse

**Pulse** is a free-to-paid conversion analytics platform built for Mer Lezun's PM team. It:

1. **Segments** free users into the four behavioral groups above using ML clustering
2. **Lets PMs** craft and launch targeted in-app upgrade messages per segment via the Campaign Editor
3. **Runs A/B tests** — control group sees a generic baseline message, treatment group sees the crafted campaign message — using Beta-Binomial Thompson Sampling to determine the winner
4. **Tracks KPIs** — overall conversion rate, churn, average revenue, and notification engagement — in a live dashboard with configurable time windows
5. **Simulates user responses** via the User Demo screen, feeding real interaction data back into the ML pipeline
