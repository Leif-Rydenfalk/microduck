# Ming relationship and the parts list — 2026-09-08

Owner: Claude coordinating session (Leif's instruction 23:50 CST: Claude owns relationship
communication; Codex lanes research and record). Companion to
`../ming-parts-request-2026-09-08/` (the list as sent, frozen) and
`../networking-2026-09-08/` (the later messages).

## What Ming has received today (WeChat desktop, "Ming Chan", all UI-observed)

| time (CST) | item | by |
|---|---|---|
| 21:32 | 13-item bilingual parts request, head first (`../ming-parts-request-2026-09-08/MESSAGE.txt`) | Codex lane |
| 21:46 | `Microduck-Ming-20260908-B.zip`, 2.7 MB, packet A inside (`../ming-handoff-2026-09-08/update-b/`) | Codex lane |
| 21:55 | **Ming: "How many virusses are in there?"** | Ming |
| 21:58 | "Haha, fair question…" plus a request for 2–3 supplier introductions | Codex lane |
| 22:00 | "I'm Leif's AI assistant, not Leif writing personally…" | Codex lane |
| 22:05 | assembly render + "Leif's AI assistant here…" caption | Codex lane |
| 22:09 | stray "l" (UI automation keystroke) | Codex lane |
| earlier | two screen-recording videos (files dated 2026-09-04) — sent outside agent evidence | ChatGPT / Leif |

No reply from Ming after 21:55 as of the 22:50 check. Joey and Tade got the AI-disclosure
introduction request (22:00) and the render (22:04/22:05). Freeze posted to every lane inbox:
`outreach-freeze-20260908-v1`.

## Will the parts list change? Yes, in four places. The rest is stable as questions.

The list was written as a *questions* list with its uncertainties stated inline, which is the
right shape, so Ming's answers will drive most changes. The engineering audits done after it was
sent (21:33 → 23:46) added evidence but resolved nothing that would change a quantity.

| item | as sent | status now | changes? |
|---|---|---|---|
| 7 servos | XL330 ×15, M288/M077 sub-type open, 3.7–6 V vs 6.6–8.2 V conflict flagged | Conflict **confirmed in the public sources** (`../servo-power-audit-2026-09-08/AUDIT.md`), not a typo; picking M077 does not fix it. Leif's XL330 vs Feetech STS3215 decision still open (`out/procurement/SOURCING-CN.md` §A: ~US$200 cheaper, local, needs CAD rework). | **Likely.** If Feetech: item 7 → STS3215 ×14 (+2 spare), item 8 connectors change, item 12 screws change. |
| 12 fasteners | "regs not verified; buy list missed M2×5, M2×10, M2.5×8" | Reconciliation: 23 modelled screws absent from the buy list; 52 servo runs classed as ISO M2 but the vendor drawing says M2 TAP into Ø1.6 pilots, 3 mm max depth, and 35 of 52 modelled runs exceed that. | **Yes.** Quantities and thread form will change once thread form is settled. Do not buy screws yet. |
| 1 Radxa ZERO 3W | 1GB/32GB not in catalogue; confirm or substitute | Fresh Shopify JSON: **every** variant unavailable at ALLNET, Arace, ameriDroid, ThinkRobotics. | **Probably.** Whatever Ming can actually find locally becomes the spec; storage need must be measured first. |
| 2 camera | IMX219 board + M12 + CSI cable, revision open | Arducam B0183-class is the candidate; Seeed 38×38 mm rejected; 22-pin↔15-pin adapter and cable length unresolved. | **Maybe.** Board/cable revision will be pinned by whatever is in stock. |
| 3 ToF | L5CX or L8CX | Still undecided. | Maybe. |
| 9 bearings | 22/16/4 ×11, 15/10/3 ×3, no 4 mm substitution | Unchanged. | No. |
| 4, 5, 6, 8, 10, 11, 13 | questions | Unchanged. | No. |

Counts that hold unless the servo decision flips: 15 servos, 11 + 3 bearings, one each of
computer, camera, ToF, battery, HAT, IMU board.

## Recommendation

Do **not** send Ming a revised list. He has one list and one unanswered question. Leif sends one
short human message (`LEIF-MESSAGE.txt`), lets Ming answer the list, and the first real change
(servo route) goes out as a two-line delta after Leif decides. Everything else is Ming's to answer.

Joey and Tade: one human line each (`LEIF-MESSAGE.txt`), no more robot content until there is
something physical to show.
