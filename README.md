# BogdewicWebSite

Source for Chris Bogdewic's personal website, deployed to GitHub Pages by a GitHub Actions CI/CD pipeline.

The `redesign/overview-and-etl` branch includes a working FEMA OpenFEMA data pipeline demo. Open `fema-disasters.html` to view its report. The daily workflow fetches public disaster declaration summaries, validates and deduplicates records, and publishes aggregate JSON to `data/fema-disasters.json`. Use Actions → **FEMA disaster data pipeline** → **Run workflow** to create the first report on this branch; daily schedule runs after the workflow is on the repository's default branch.

The report is descriptive, not an emergency alert. The data source refreshes independently of this pipeline.
