# E-Regami — Foldable Printed Electronics on Cellulose

> Characterisation of silver ink traces on folded cellulose substrates using origami and kirigami fold patterns.

**Author:** Pablo Prieto Vidal  
**Institution:** Eindhoven University of Technology · Department of Industrial Design  
**Supervisor:** Amy K.M. Winters  
**Programme:** Master Industrial Design · M12 Research · Sensory Matters squad  
**Year:** 2026  
**Archive:** [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20625501.svg)](https://doi.org/10.5281/zenodo.20625501)

---

## Overview

E-Regami investigates the electromechanical behaviour of printed silver  ink traces (Ail Arian ReSilver 102) on uncoated cellulose substrates subjected to repeated folding. Five fold patterns drawn from origami and kirigami: Single Crease, Accordion, Miura-ori, Kirigami, and Waterbomb, are combined with three trace orientations (0°, 45°, 90°) to produce 22 characterised specimens, each tested across 100 fold cycles.

The research is framed for industrial designers without electronics expertise, providing a reference dataset and practical toolkit for prototyping foldable printed circuits on paper.

**Key findings:**
- Miura-ori at 45° diagonal orientation is the only configuration achieving Excellent classification (ΔR/R₀ < 0.3) across 100 cycles
- Valley routing fails categorically across all patterns regardless of orientation
- 5 mm kirigami relief cuts at the crease edge are the most effective stress-relief geometry tested

---

## Repository Structure

```
eregami-foldable-printed-electronics/
│
├── README.md
├── LICENSE-code          # MIT — applies to /characterisation-tool
├── LICENSE-data          # CC BY 4.0 — applies to /dataset, /fabrication-guide, /sample-library
│
├── dataset/
│   └── Datasheet_v3.xlsx         # Raw measurements, experiment log, printer calibration log
│                                 # Sheets: Experiment Log · Medidas · Printer Calibration Log
│
├── fabrication-guide/
│   └── folding_printing_guide_v2.html    # Step-by-step fabrication protocol
│                                         # Covers all 5 fold patterns, print settings,
│                                         # measurement procedure, and specimen index
│
├── sample-library/
│   └── eregami_sample_library.pdf        # Visual reference for all 22 specimens
│                                         # Electromechanical data, photos, and ratings
│
└── characterisation-tool/
    ├── arduino/
    │   └── eregami_resistance.ino        # Real-time resistance measurement via voltage divider
    └── processing/
        └── eregami_visualiser/
            └── eregami_visualiser.py    # Live graph + interactive 3D fold model
```

---

## Dataset

**File:** `dataset/Datasheet_v3.xlsx`

The dataset contains three sheets:

| Sheet | Contents |
|---|---|
| Experiment Log | 22 specimens · fold pattern · trace orientation · R₀ · R at each checkpoint · ΔR/R₀ · failure mode |
| Medidas | Raw individual measurements (10 per checkpoint) · Grubbs outlier test (ISO 5725-2, α = 0.05) · mean · U₉₅% |
| Printer Calibration Log | 11 calibration specimens (P2–P10 + P7\_C, P10\_C) · Voltera V-One parameters · ink formulation comparison |

**Measurement protocol:** 10 resistance readings per checkpoint (flat, @10, @25, @50, @100 cycles) using an OW18A True RMS multimeter. Outlier exclusion via Grubbs' test (ISO 5725-2). Expanded uncertainty U₉₅% reported as t·s/√n.

**Classification thresholds:**

| Rating | ΔR/R₀ | Interpretation |
|---|---|---|
| Excellent | < 0.3 | Functional conductivity retained |
| Acceptable | 0.3 – 0.7 | Usable with resistance budget |
| Marginal | 0.7 – 1.0 | Unpredictable; static use only |
| Degraded | > 1.0 | Signal too degraded |
| FAIL | — | Open circuit before 100 cycles |

---

## Hardware & Materials

| Component | Specification |
|---|---|
| Printer | Voltera V-One PCB printer |
| Ink | Ail Arian ReSilver 102 (silver nanoparticle, [ailarian.co.uk](https://ailarian.co.uk)) |
| Substrate (primary) | Uncoated cellulose 80 g/m² |
| Substrate (KR\_TWISTING only) | Uncoated cellulose 160 g/m² |
| Multimeter | OW18A True RMS |
| Microcontroller | Arduino (characterisation tool) |

**Printer settings (production — P10):**  
Nozzle: 0.2 mm · Z height: 0.2 mm · Speed: 150 mm/min · Kick: 0.05 · Rheology: 0.50 · Antistrings: 0.1

---

## Fabrication Guide

**File:** `fabrication-guide/folding_printing_guide_v2.html`

Open in any browser. Covers:
- Voltera V-One print bed layout and specimen placement
- Universal print rules (trace clearance, pad size, curing)
- Per-pattern instructions: Single Crease, Accordion, Miura-ori, Kirigami, Waterbomb
- Measurement protocol (static angles + cycle checkpoints)
- Complete specimen index (22 specimens with ΔR/R₀ and rating)

---

## Characterisation Tool

**Directory:** `characterisation-tool/`

A two-part tool built for demo day:
- **Arduino sketch:** reads resistance in real time via voltage divider circuit
- **Processing sketch:** live graph + interactive 3D model of the specimen that responds to fold angle

> Note: the tool was developed as a demonstration and has not been validated for metrological accuracy. For replication of the characterisation protocol, use the measurement procedure documented in the fabrication guide.

---

## Citing This Work

If you use this dataset or materials in your research, please cite:

```bibtex
@inproceedings{prietovidal2026eregami,
  author    = {Prieto Vidal, Pablo},
  title     = {E-Regami: Characterising Silver Nanoparticle Ink Traces
               on Folded Cellulose for Foldable Printed Electronics},
  booktitle = {TBD},
  year      = {2026},
  doi       = {[Paper DOI when available]}
}

@dataset{prietovidal2026eregami_data,
  author    = {Prieto Vidal, Pablo},
  title     = {E-Regami: Foldable Printed Electronics Dataset
               and Pattern Library},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20625501},
  url       = {https://doi.org/10.5281/zenodo.20625501}
}
```

---

## Licences

| Material | Licence |
|---|---|
| Characterisation tool (code) | [MIT](LICENSE-code) |
| Dataset, fabrication guide, sample library | [CC BY 4.0](LICENSE-data) |

---

## Acknowledgements

Material support: Ali Arian ([Ail Arian](https://ailarian.co.uk)) · ReSilver 102 ink samples  
Supervision: Amy K.M. Winters · TU/e Industrial Design  
Voltera workshop: e-textiles and wearables programme
