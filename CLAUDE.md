# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is the **Patient Access Center (PAC) Master Guide** for US Eye — a documentation and tooling repository used by a centralized scheduling hub serving multiple Florida-based eye care practices within the US Eye network. The content is published via GitBook and GitHub Pages.

The four practice groups are:
- **CFS** – Center For Sight (11 offices, Sarasota to Naples)
- **SFEC** – Southwest Florida Eye Care (3 offices, Fort Myers to Naples)
- **LEA** – Lake Eye Associates (5 offices + ASC, The Villages area)
- **RHC** – Retina Health Center (2 offices, Fort Myers to Naples)

## Repository Structure

```
/
├── README.md                          # Master guide (GitBook entry point, ~100KB)
├── SUMMARY.md                         # GitBook table of contents
├── Provider Reference Guide.md        # All providers: specialties, locations, NPIs
├── Location Reference Guide.md        # All locations: addresses, phones, hours
├── Dilation Key.md                    # Dilated vs. non-dilated appointment reference
├── Insurance_Guide_By_Provider.md     # Index: insurance status per doctor
├── Insurance_Guide_By_Insurance.md    # Index: providers per insurance plan
├── physician-relations-referral-coordination.md  # Co-managing OD referral table
├── insurance_docs/                    # ~200+ individual markdown files, one per doctor or insurance plan
├── ai-agent/                          # AI assistant reference docs (FAQ, definitions, abbreviations)
├── readme/                            # GitBook sub-pages (BCBS updates, etc.)
├── .github/workflows/                 # CI: GitHub Pages deploy + auto-date update on README
├── create_insurance_guides_fixed.py   # Script to regenerate insurance_docs/ from Excel
├── location_map.py                    # Script to regenerate locations_map.html from Location Reference Guide.md
├── US Eye Insurance Guide.xlsx        # Source of truth for all insurance participation data
├── Insurance_FAQ.csv                  # FAQ source data
└── locations_map.html                 # Interactive Folium map of all practice locations
```

## Python Scripts

### `create_insurance_guides_fixed.py`

Reads `US Eye Insurance Guide.xlsx` and regenerates all files in `insurance_docs/` plus the two index files (`Insurance_Guide_By_Provider.md` and `Insurance_Guide_By_Insurance.md`).

**To run:**
```bash
pip install -r requirements.txt
python create_insurance_guides_fixed.py
```

Dependencies: `pandas`, `openpyxl`

The script processes five Excel sheets: `Center for Sight`, `Center for Sight-Naples`, `Lake Eye`, `Retina Health Center`, `SW FL Eye`. It detects doctor columns dynamically, generates per-doctor markdown files in `insurance_docs/`, and logs to `insurance_guide_generation.log`.

**When to run:** Whenever `US Eye Insurance Guide.xlsx` is updated. The generated files should be committed after running.

### `location_map.py`

Parses `Location Reference Guide.md` and regenerates `locations_map.html` (an interactive Folium map).

**To run:**
```bash
pip install folium
python location_map.py
```

Coordinates for all locations are hardcoded in `HARDCODED_COORDS`. If a new location is added to `Location Reference Guide.md`, add its coordinates to that dictionary.

## CI / GitHub Actions

- **`pages.yml`**: Builds with Jekyll and deploys to GitHub Pages on every push to `main`/`master`. The `_config.yml` excludes `README.md` from Jekyll processing (GitBook handles it separately).
- **`update-readme-date.yml`**: Automatically updates the `**Last Update:**` line in `README.md` whenever `README.md` is pushed. Commits with `[skip ci]` to avoid loops.

## Key Conventions

### Insurance Data Flow
The Excel file (`US Eye Insurance Guide.xlsx`) is the authoritative source. Never manually edit files in `insurance_docs/` — always update the Excel file and re-run `create_insurance_guides_fixed.py`. The `Last Updated` timestamp in the index files is derived from the Excel file's filesystem modification time.

### Insurance Status Terms
- **PAR** – Provider has a direct contract with the payer (participating)
- **Non-PAR-OON Benefits** – No contract, but PPO out-of-network benefits may apply
- **Non-PAR** – No contract, patient pays self-pay rates; HMOs have no OON benefits

### EHR / Scheduling Systems
- **NextGen** – Primary EHR for CFS, SFEC, LEA
- **ICP / NexTech** – Used by some practices (e.g., SFEC for surgical coordinator tasks)
- **Phreesia** – Third-party eligibility & benefits verification tool

### GitBook
Content is published to GitBook. `SUMMARY.md` controls the navigation tree. GitBook-specific syntax (e.g., `{% hint %}`, `{% file %}`) appears in some markdown files and is not standard markdown — do not strip it.

### Filename Sanitization
Files in `insurance_docs/` use sanitized names: special characters replaced with `_`, truncated to 100 chars (first 50 + `_` + last 50). This logic lives in `sanitize_filename()` in `create_insurance_guides_fixed.py`.
