# usage-status

The user invoked **usage-status** to **see Cursor plan usage** in the real account UI. This chat **cannot** read quotas from Cursor’s servers.

## Do this

1. **Run** from the **workspace root** (project script):

   ```bash
   bash scripts/open-cursor-usage.sh
   ```

   If that file is missing, use the personal copy:

   ```bash
   bash "$HOME/.cursor/scripts/open-cursor-usage.sh"
   ```

2. **Reply in one or two sentences** — e.g. opened the page; sign in if prompted; check **Usage** / **Billing** in **Cursor Settings** (`Ctrl+Shift+J` → Account) if needed.

## If the command fails

Tell them to open **Cursor Settings** (`Ctrl+Shift+J`) → **Account** / **Usage**, or [cursor.com](https://cursor.com) while signed in.

## Optional

To open a different URL: `CURSOR_USAGE_URL='https://cursor.com' bash scripts/open-cursor-usage.sh`
