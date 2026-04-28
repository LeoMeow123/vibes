# Paper Brain

Searchable research paper library with DOI/URL lookup, structured annotations, citation formatting, and Claude batch annotation.

## Features

- **Add papers**: Paste a DOI, URL (Nature, Science, Cell, PubMed, bioRxiv), or title → auto-fills metadata from CrossRef
- **Structured fields**: species/model, brain region, study type, methods, key findings, notes, project tags
- **7 study types**: single-cell atlas, AD/neurodegeneration, LC/norepinephrine, behavioral methods, computational, aging, review
- **Filter chips**: by type, species (mouse/human/rat), and brain region (LC/PFC/etc.)
- **Full-text search**: across all fields simultaneously
- **Sortable columns**: title, year, journal, type, species, region
- **Citation formatting**: one-click Nature, Cell, or Science format citations with auto-copy
- **DOI links**: clickable DOI/URL next to journal in the table
- **Batch Claude**: generate prompts for Claude.ai to extract metadata from abstracts in bulk
- **Sync**: pull latest `papers.json` from server without losing locally-added papers
- **Import/Export**: JSON backup for GitHub/NAS

## Live Demo

[Launch Paper Brain](https://leomeow123.github.io/vibes/paper-brain/)

## URL Lookup

Paste any of these formats into the lookup field:

| Format | Example |
|--------|---------|
| DOI | `10.1038/s41586-024-07606-7` |
| doi.org | `https://doi.org/10.1038/...` |
| Nature | `https://www.nature.com/articles/s41586-024-07606-7` |
| Science | `https://www.science.org/doi/10.1126/science.adf7044` |
| Cell | `https://www.cell.com/cell/fulltext/S0092-8674(23)00973-X` |
| PubMed | `https://pubmed.ncbi.nlm.nih.gov/31042697/` |
| bioRxiv | `https://www.biorxiv.org/content/10.1101/...` |
| Title | `Single-cell transcriptomic analysis of Alzheimer's disease` |

## Citation Formats

Click any paper → click Nature / Cell / Science button → citation copies to clipboard.

- **Nature**: Author1, I.N., Author2, I.N. et al. Title. *Journal* (Year). DOI
- **Cell**: Author1, I.N., and LastAuthor, I.N. (Year). Title. *Journal*. DOI
- **Science**: I.N. Author1, I.N. Author2, Title. *Journal* (Year). DOI

## Batch Claude Workflow

For bulk annotation without an API key (uses your Claude Max plan):

1. Go to **Batch Claude** tab → select papers missing findings → Generate Prompt
2. Copy the prompt → paste into Claude.ai
3. Claude returns structured JSON with species, region, methods, findings
4. Paste the JSON back → Paper Brain auto-fills the fields

## Data Storage

- Papers stored in browser `localStorage` (persistent across sessions)
- On first visit, auto-loads `papers.json` from the server
- **Sync** button pulls server updates without overwriting locally-added papers
- **Export JSON** for backup to GitHub/NAS
- **Import JSON** merges with deduplication

## Dependencies

None — runs entirely in browser using CrossRef API (free, no key needed).
