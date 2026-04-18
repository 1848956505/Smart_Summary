# Smart Summary UI Redesign Design

Date: 2026-04-18
Scope: Global UI direction plus the memo workspace as the first reference page
Status: Draft for review

## Goal

Reframe Smart Summary from a feature-complete internal tool into a more polished flagship product with a coherent visual system. The redesign should improve perceived quality, hierarchy, and usability without breaking the current product logic.

The memo workspace is the first redesign target because it is the most complex and most valuable page. It will act as the reference implementation for the rest of the product.

## Design Decision Summary

### Chosen rollout strategy

Use a staged redesign.

- First redesign the memo workspace until it feels right.
- Use the memo workspace as the visual and structural reference for other pages.
- Apply the resulting language to dashboard, generate, history, and settings in later iterations.

This approach reduces risk, prevents full-site drift, and gives the product a validated flagship page before wider rollout.

### Chosen product direction

The memo workspace should be designed as a flagship efficiency workspace with a warm editorial feel.

- Product type: flagship product
- Memo page type: flagship efficiency workspace
- Visual tone: warm editorial
- Visual intensity: restrained refinement
- Primary content: daily fragment flow
- Structural core: calendar timeline
- Left panel role: semi-immersive reference rail

## Global UI Language

### Product shell

The product shell should feel like a premium software product rather than a backend admin panel.

- Left rail style: flagship product sidebar
- Layout strategy: mixed width
- Typography style: refined product typography
- Container style: soft layering
- Color style: warm branded restraint

### Sidebar principles

The global sidebar is part of the product shell, not the main content.

- It should be visually calm and stable.
- It should carry product identity without becoming a logo-heavy brand block.
- It should contain only first-level navigation and essential account actions.
- It should be separated from the content area by material difference and spacing, not heavy borders.

Desired feel:

"Like a polished productivity product shell, but warmer and more editorial than a cold enterprise dashboard."

### Layout principles

Use two page width modes inside one unified shell.

- Workspace pages: use wider layouts to support complex flows and denser operations.
- Standard pages: use a more controlled reading width for clarity and polish.

Rules:

- Shell spacing and starting lines should stay consistent across page types.
- Width changes should follow page purpose, not designer preference.
- Wide layouts should still feel intentional, not stretched.

### Typography principles

Typography should feel designed, calm, and premium.

- Titles should be sparse and meaningful.
- Body text should prioritize readability and rhythm.
- Metadata should stay quiet and supportive.
- Heading levels, body sizes, and helper text sizes must be fixed globally and reused consistently.

Desired feel:

"The product speaks like a premium software product, not a form-driven admin panel."

### Container principles

Use soft layering instead of obvious card stacking.

- Containers exist, but should not dominate the page.
- Separation should rely on spacing, background shifts, and soft shadow rather than heavy outlines.
- Only important areas should feel clearly lifted from the surface.
- A page should not make every section feel equally heavy.

### Color principles

Color should be restrained and warm.

- Most of the interface should rely on warm off-white, pale gray, and soft neutral tones.
- Brand color should be used sparingly for active states, main actions, and important anchors.
- Status colors must be clear, but should not make the page feel like a monitoring dashboard.
- Large regions of saturated color should be avoided.

Desired feel:

"Warm branded product, not cold admin UI and not overly expressive marketing UI."

## Memo Workspace Reference Design

### Role of the page

The memo workspace is not just a CRUD page. It is the product's main recording and organizing workspace.

The page should feel like a working surface for turning daily fragments into weekly structure and eventual weekly summaries.

### Core page structure

The page should follow a left-quiet, right-strong structure.

#### 1. Left semi-immersive reference rail

Purpose:

- Select folders
- Select week records
- Perform a small set of management actions

Behavior and presentation:

- Narrower and quieter than a traditional dashboard sidebar
- Folder records as primary level
- Week records as secondary level
- Actions are present but visually restrained
- Selection relies on spacing, weight, soft background shift, and subtle highlight instead of loud contrast

The left rail should feel like a project drawer, not a utility control panel.

#### 2. Top week context bar

Purpose:

- Show the current week title
- Show the date range
- Show a small set of key status metrics
- Surface the highest-priority action

Behavior and presentation:

- More like an editor context bar than a large stats card
- The main CTA is "generate weekly summary"
- Secondary actions should be reduced in visual weight and not compete equally with the main CTA
- Stats should read like context metadata, not dashboard widgets

The top bar should answer:

- Which week am I in?
- What is its current state?
- What is the most important next action?

#### 3. Middle daily fragment timeline

Purpose:

- Act as the main stage of the page
- Organize one week into readable daily chapters
- Support browse, edit, reorder, and review workflows

Behavior and presentation:

- Keep the calendar-timeline structure because it is already the most valuable page pattern
- Elevate each day into a chapter-like section
- Keep the date anchor visible and refined
- Treat fragments as high-quality content entries rather than generic business cards

The middle region should own the majority of visual attention on the page.

The intended feeling is:

"I am organizing a week of real work, not scanning a system list."

#### 4. Bottom quick capture bar

Purpose:

- Allow fast, low-friction fragment entry at any time
- Keep capture close to the main timeline without interrupting it

Behavior and presentation:

- Fixed inside the main workspace area
- Calm by default
- Gains presence on focus
- Supports one-line to multi-line expansion
- Includes one primary submit action and one low-emphasis route to detailed entry

The quick capture bar should feel like a lightweight editor entry point, not a chat box and not a full form module.

## Memo Page Visual Rules

### Hierarchy rules

- The daily fragment timeline is always the visual lead.
- The left rail organizes, but does not dominate.
- The top context bar informs, but does not perform as a hero section.
- The bottom quick capture bar stays accessible, but should not visually overpower the content stage.

### Separation rules

- Use weak boundaries.
- Prefer tonal shifts, material differences, and spacing over thick borders.
- Keep the page visually continuous.

### Fragment card rules

- Fragment cards should feel like refined content objects.
- Emphasize reading flow first, operations second.
- High-frequency actions should remain easy to access, but lower-frequency controls should be quieter.
- Cards should not resemble generic admin modules.

### Action rules

- Only a small number of actions should look important.
- The main page action is generating the weekly summary.
- The main high-frequency local action is quick fragment capture.
- Other actions should be visually compressed through iconography, lower contrast, or overflow patterns.

### Material rules

- Soft shadows only
- Medium-to-large radius, but not exaggerated
- Light transparency or soft blur only in selective places such as the quick capture bar or context bar
- Never apply elevated treatment to every block on screen

## Mapping to Existing Product Areas

The memo workspace will define the product language that later pages should inherit.

### Dashboard

- Should reuse the shell, typography, spacing, and soft layering rules
- Should feel like a refined overview page, not a card collage

### Generate

- Should become a calmer focused workspace
- Should borrow context handling and restrained action hierarchy from the memo page

### History

- Should inherit the wider workspace layout mode
- Should use the same quiet metadata language and content-first list/detail treatment

### Settings

- Should use the standard page width mode
- Should become more editorial and structured, less like a default component form

## In Scope for the First Implementation

- Global shell direction for sidebar, width rules, typography, containers, and color
- Memo workspace layout restructuring
- Memo workspace visual redesign
- Memo workspace component restyling for rail, context bar, timeline, and quick capture bar

## Out of Scope for the First Implementation

- Full product-wide redesign in one pass
- Business logic changes to memo workflows
- New information architecture beyond what is needed to support the visual redesign
- Backend or schema changes

## Acceptance Criteria

The memo workspace redesign is successful when:

- The page clearly feels like the visual flagship of the product
- The daily timeline is the obvious center of attention
- The left rail and top context area support the workflow without competing with the main content
- Quick capture feels faster and more natural than the current implementation
- The page feels premium and coherent without becoming flashy
- The result is strong enough to serve as the design reference for the rest of the app

## Implementation Guidance

When implementation begins, prefer a medium structural refactor rather than a full rebuild.

- Keep the successful calendar timeline concept
- Reorganize hierarchy and spacing before inventing new features
- Re-skin components only after the new page structure is stable
- Derive reusable shell and surface patterns from the memo page for later use elsewhere

## Risks and Guardrails

### Risk: over-designing the page

Guardrail:

Keep the page restrained. It should feel premium, not flashy.

### Risk: making the memo page too soft and losing efficiency

Guardrail:

Preserve strong operational clarity in selection, actions, and status, even while reducing visual noise.

### Risk: redesigning all pages before the language is proven

Guardrail:

Do not expand the redesign across the product until the memo page direction is validated.

## Next Step

After this design document is reviewed and approved, create an implementation plan focused on:

- Global shell foundations needed for later reuse
- Memo workspace redesign sequence
- Verification checkpoints before applying the language to the rest of the product
