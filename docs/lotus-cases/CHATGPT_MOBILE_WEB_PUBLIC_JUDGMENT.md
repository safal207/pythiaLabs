# ChatGPT mobile-web public Lotus judgment

**Verdict:** `ALLOW_BOUNDED_DIAGNOSTIC`  
**Case:** `chatgpt-mobile-web-public-2026-07-21`  
**Source:** `safal207/LiminalQAengineer` PR `#106`  
**Exact source head:** `2407be212e19a393fcd0d8dd33d9fe444aea663b`

## Decision

The source audit supports a narrow, human-reviewed conclusion:

- the signed-out ChatGPT mobile-web entry passed the bounded route, horizontal-layout, compact-height, primary-control, layout-stability and event-delivery checks;
- a distinct mobile-user-agent delivery branch is confirmed, but is not a defect;
- one repeated first-party `console.error` exists on the public mobile login page;
- no visible login failure, uncaught page error, security impact or authenticated-chat impact was established.

`ALLOW_BOUNDED_DIAGNOSTIC` permits the P3 diagnostic to be retained for first-party engineering review. It does not permit a claim that login is broken, users are blocked, telemetry is lost, the mobile web is inferior to the native app, or a security vulnerability exists.

## Confirmed passes

1. Five public home profiles returned HTTP `200`.
2. No horizontal overflow was detected in either round.
3. The signed-out composer remained visible at `412×915` and `412×520`.
4. Critical mobile controls exposed `44×44` CSS-pixel boxes in the tested state.
5. The mobile login page retained provider, email and Continue choices without horizontal overflow.
6. Public-home CLS stayed between `0` and `0.0004` in the observation window.
7. `/unauth-mweb/events/` POSTs received successful HTTP `200/204` responses.

A pass is scoped to the exact signed-out profiles and observation window. It is not a global quality claim.

## Allowed observation

### Distinct mobile branch — `CONFIRMED_ARCHITECTURE_NOT_DEFECT`

At the same `412×915` viewport, desktop and Android mobile user-agents received different signed-out headings, header structure and CTA state. This establishes a mobile-user-agent branch that requires independent regression and experiment coverage.

It does not establish a user problem.

## Allowed diagnostic

### Public mobile-login console signal — `P3_DIAGNOSTIC`

The focused probe reproduced one first-party `console.error` in both rounds:

- console text: `JSHandle@error`;
- serialized values: empty object and `undefined`;
- first-party minified bundle source;
- no uncaught page error;
- no visible login-form failure.

The correct statement is:

> A stable first-party console diagnostic exists on the public mobile login page; its semantic cause and user impact are unknown.

The correct next action is first-party source-map resolution and explicit error-code logging, followed by a repeat of the public console-cleanliness check.

## Rejected claims

The judgment blocks the following:

- `/unauth-mweb/events/` delivery failed;
- public login is broken;
- authentication is unavailable;
- the console signal exposes a security vulnerability;
- users lose data or telemetry;
- the mobile composer is obstructed;
- the page has duplicate visible headings;
- the public mobile page has a confirmed touch-target accessibility failure;
- native-app behaviour is proven by the mobile-web run;
- authenticated long-chat, streaming, attachment, sidebar, Search, Projects, Work, billing, settings or offline behaviour has been assessed.

## Rejected detector outputs

- Event-request failure: rejected because successful HTTP `200/204` responses preceded the browser loading-aborted signal.
- Composer overlap: rejected after screenshot review showed an ancestor container rather than obstruction.
- Duplicate visible heading: rejected by the controlled browser matrix.
- Raw small-target count: insufficient because critical icons met the threshold and inline/link context was not adjudicated as a failed task.

## Unknowns preserved

- real virtual-keyboard and browser-chrome interaction;
- authenticated long-conversation navigation;
- streaming interruption and reconnect recovery;
- file, image, camera and attachment states;
- mobile Search sources, widgets, Projects, Work and plan-limit states;
- TalkBack, browser zoom and external-keyboard tasks;
- the semantic meaning of the opaque login Error object.

## Pythia boundary

This packet is public and audit-only. It does not log in, submit a prompt, access a private conversation, contact OpenAI, approve an external report, claim a vulnerability, deploy or merge.

Machine-readable judgment: `examples/lotus-cases/chatgpt-mobile-web-public-judgment-v1.json`.
