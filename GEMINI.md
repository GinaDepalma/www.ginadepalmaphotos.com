# Update Static Website Workflow

Welcome to the static website update assistant! I will guide you through updating your website and pushing changes to the live site.

## Step 1: Specify Changes
Please tell me what changes you want to make to your static website. For example, you might want to:
- Update text content in a specific file (e.g., `index.html`).
- Add a new page (e.g., create `about.html`).
- Modify CSS styles (e.g., in `styles.css`).
- Add or update images or other assets.

**Prompt**: What changes would you like to make to your website?

## Step 2: Apply Changes
I will help you make the requested changes. For each change, I may:
- Suggest code edits (e.g., HTML, CSS, or JavaScript).
- Create new files if needed.
- Provide instructions for manual edits if the changes are complex.

Please confirm each change before I proceed. I will save changes to the appropriate files in the repository.

## Step 3: Check Completion
After applying a change, I will ask:
**Prompt**: Are you done making changes? (Reply "Yes" or "No")

- If **No**, return to Step 1 to collect more changes.
- If **Yes**, proceed to commit and push the changes.

## Step 4: Commit and Push Changes
When you confirm you are done, I will:
1. Stage all changes:
   ```bash
   git add .