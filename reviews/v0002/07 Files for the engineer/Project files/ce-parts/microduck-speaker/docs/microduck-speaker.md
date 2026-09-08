# Microduck head speaker — 35 × 25 × 7 mm box; exact part CANNOT DETERMINE

*Pollen's MJCF carries a 12-triangle placeholder `speaker` 35.0 × 25.0 × 7.0
mm in the head (`docs/PARTS.md` row 38). The codec is a TLV320AIC3104 (I2C
0x18, ALSA `plughw:aic3104`); what drives the speaker — the codec's own
output or an amplifier on the unpublished HAT — is CANNOT DETERMINE
(`docs/ELECTRONICS-AND-SOFTWARE.md` §7).*

## The representative, said plainly

A commodity **"3525" 8 Ω 2 W cavity speaker** — 35 × 25 × 6.8 mm, two-wire
lead with a 1.25 mm 2-pin connector. It is chosen because its envelope
matches Pollen's box in plan exactly and within 0.2 mm in height, **not**
because any source says Pollen fits one. Its maker is anonymous; **no
manufacturer datasheet exists**, so the figures are a reseller's spec table.

| doc | what | fetched |
|---|---|---|
| `docs/abra-spk-3525-2w-gh.html` | ABRA Electronics `SPK-3525-2W-GH 3525 8R 2W Box Speaker with GH1.25 Terminal Wire Price: USD$ 2.95` — the spec table quoted in `electrical.part.json` | 2026-09-02, HTTP 200, sha256 `4e9adf65…d8dd1` |
| `docs/thingbits-xhxdz-3525-8r2w.html` | a second 3525 (`Model XHXDZ-3525-8R2W Dimensions 35 × 25 × 6.2 mm Rated Impedance 9Ω ±15% Rated Power 2W`) — disagrees with ABRA on impedance and F0; recorded, not averaged | 2026-09-02, sha256 `bd98f5f1…ee1d82` |
| `docs/samesky-cms-35208n-datasheet.pdf` | Same Sky CMS-35208N — the nearest speaker **with** a manufacturer sheet: 35.5 × 20.5 × 8.0 mm, 8 Ω, 1 W, 720 Hz, 98 dB (read off the rendered p.1); DISCONTINUED. Wrong width — a contrast | 2026-09-02, sha256 `689c9d51…f6376` |

ABRA, verbatim: `Size: 35mm x 25mm x 6.8mm.` · `Impedance: 8 Ohm ± 15% at
1 kHz and 3.46V.` · `Rated Power Input: 2.0W.` · `Maximum Power Input: 2.5W.`
· `Resonance Frequency: 980 Hz ± 20% at 1.0V.` · `SPL (Sound Pressure
Level): 88 dB ± 3dB at 2.0W/0.1m, measured at 800Hz, 1000Hz, 1200Hz, and
1500Hz average.` · `Polarity: The diaphragm moves forward when a positive DC
voltage is applied to the "+" terminal (red).`

`tools/datasheet-quotes-check.py microduck-speaker` re-finds each quote in the
saved page.

## What settles it

A teardown photo of the head with the speaker's label, or Pollen naming the
part and the amplifier. Until then the folder's verdict is CANNOT DETERMINE
and any rebuild fits the representative on its own responsibility.

Standards: none. No `standard` ledger row.
