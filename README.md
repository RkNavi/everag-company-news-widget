# Ever.Ag Company News iframe widget

This is a small static website that displays the Ever.Ag Company News RSS feed. It is designed to be hosted with GitHub Pages and embedded in Confluence using the iFrame macro.

## What it does

- Reads the existing FetchRSS feed.
- Converts the feed to `feed.json` with a scheduled GitHub Actions workflow.
- Displays responsive news cards with titles, dates, summaries, images, and links.
- Avoids browser CORS problems because the HTML and JSON are hosted together.
- Requires no RSS widget subscription.

## Setup

### 1. Create the repository

1. Sign in to GitHub.
2. Create a new **public** repository named `everag-company-news-widget`.
3. Extract this ZIP file.
4. Upload all extracted files and folders to the repository. Preserve the `.github/workflows` folder.

Using GitHub Desktop is the easiest way to preserve all folders, including `.github`.

### 2. Run the feed update once

1. Open the repository's **Actions** tab.
2. Select **Update company news**.
3. Select **Run workflow**.
4. Confirm that the workflow finishes successfully.

The workflow then runs once per day and can also be run manually whenever a new Ever.Ag article is published.

### 3. Enable GitHub Pages

1. Open **Settings** in the repository.
2. Select **Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select the `main` branch and the `/ (root)` folder.
5. Save.

GitHub will provide a site address similar to:

```text
https://YOUR-GITHUB-USERNAME.github.io/everag-company-news-widget/
```

### 4. Add it to Confluence

1. Edit the Confluence **Company News** page.
2. Add the `/iframe` macro.
3. Paste the GitHub Pages site address—not the RSS address.
4. Suggested settings:
   - Width: `100%`
   - Height: `950` to `1200` pixels
   - Border: hidden
5. Publish the Confluence page.

## Important limitations

The FetchRSS free plan is still part of this setup. Its current free limits include a 24-hour feed refresh and five posts in the feed. The daily workflow accesses the feed regularly, which also helps prevent it from being considered unused.

The GitHub repository and Pages site are public on GitHub Free. Only use this package for the public Ever.Ag news feed; do not add internal company information, credentials, API keys, or private Confluence content.

## Customization

Edit `styles.css` to change fonts, spacing, card layout, and colors. The main brand color is currently set as `#274857` near the top of the file.
