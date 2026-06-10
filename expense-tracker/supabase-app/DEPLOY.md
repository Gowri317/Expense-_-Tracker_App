# Deployment Guide — Expense Tracker (Supabase + Netlify)

This guide walks you through deploying your migrated Expense Tracker. No backend server needed!

---

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up / log in.
2. Click **"New Project"**.
3. Choose your organization, give it a name (e.g., `expense-tracker`), set a database password (save it somewhere), and pick a region close to you.
4. Wait ~2 minutes for the project to be created.

---

## Step 2: Run the SQL Schema

1. In your Supabase dashboard, go to **SQL Editor** (left sidebar).
2. Click **"New Query"**.
3. Open the file `schema.sql` from this folder and **copy-paste the entire contents** into the SQL editor.
4. Click **"Run"** (or Ctrl+Enter).
5. You should see "Success. No rows returned" — this means all tables, indexes, RLS policies, and default categories have been created.

### Verify
- Go to **Table Editor** in the left sidebar.
- You should see 4 tables: `categories`, `expenses`, `incomes`, `budgets`.
- Click on `categories` — you should see 8 default categories (Food, Transport, Bills, etc.).

---

## Step 3: Configure Authentication

1. In the Supabase dashboard, go to **Authentication** → **Providers**.
2. Ensure **Email** provider is enabled (it is by default).
3. **(Recommended for testing)**: Go to **Authentication** → **Settings** → under **Email Auth**, **disable "Confirm email"** (toggle it OFF). This lets users register and log in immediately without email verification.
4. You can always re-enable email confirmation later for production.

---

## Step 4: Get Your Supabase Credentials

1. Go to **Settings** → **API** (or click the gear icon → API).
2. You need two values:
   - **Project URL** — looks like `https://xyzcompany.supabase.co`
   - **`anon` public key** — the long JWT string under "Project API keys" → `anon` → `public`

---

## Step 5: Paste Credentials into app.js

Open `supabase-app/app.js` and replace the placeholder values at the top:

```javascript
const SUPABASE_URL  = 'https://YOUR-PROJECT-ID.supabase.co';   // ← paste your Project URL
const SUPABASE_ANON = 'eyJhbGciOiJIUzI1NiIsInR5cCI6...';      // ← paste your anon key
```

**Save the file.**

---

## Step 6: Test Locally

1. Open `supabase-app/index.html` directly in your browser (double-click the file, or use a local server).
   
   **Option A — Direct open**: Just double-click `index.html`. Works for most browsers.
   
   **Option B — Local server** (recommended): Run one of these in the `supabase-app` folder:
   ```bash
   # Python
   python -m http.server 8080
   
   # Node.js (if you have npx)
   npx serve .
   ```
   Then open `http://localhost:8080`.

2. Test the following:
   - ✅ Register a new account (email + password)
   - ✅ Login with the account
   - ✅ Add an expense → check it appears in History
   - ✅ Add income → check it appears in History
   - ✅ Set a budget → check it appears on the Dashboard and Budgets pages
   - ✅ Edit and delete transactions in History
   - ✅ Logout → confirm redirect to auth page

---

## Step 7: Deploy to Netlify

### Option A: Drag and Drop (Easiest)

1. Go to [https://app.netlify.com](https://app.netlify.com) and sign up / log in.
2. Click **"Add new site"** → **"Deploy manually"**.
3. Drag the entire `supabase-app` folder into the upload area.
4. Done! Netlify will give you a URL like `https://random-name.netlify.app`.

### Option B: GitHub Deploy (Auto-updates)

1. Push the `supabase-app` folder to a GitHub repository.
2. In Netlify, click **"Add new site"** → **"Import an existing project"** → connect GitHub.
3. Select your repo.
4. Set **"Publish directory"** to `supabase-app` (or `/` if the repo only contains these files).
5. Click **"Deploy site"**.
6. Every time you push to main, Netlify will auto-deploy.

---

## Step 8: Update Supabase Auth Redirect URL

After deploying to Netlify:

1. Go to your Supabase dashboard → **Authentication** → **URL Configuration**.
2. Set **Site URL** to your Netlify URL (e.g., `https://your-app.netlify.app`).
3. Add the same URL to **Redirect URLs**.
4. Save.

---

## File Structure

```
supabase-app/
├── index.html      ← Single-page app (all screens)
├── style.css       ← Complete CSS design system
├── app.js          ← Application logic (Supabase SDK)
├── schema.sql      ← Database schema (run in Supabase SQL Editor)
├── _redirects      ← Netlify SPA routing
└── DEPLOY.md       ← This file
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "Invalid API key" error | Double-check you pasted the **anon** key (not the service_role key) |
| Can't register / "Email not confirmed" | Go to Supabase → Auth → Settings → disable "Confirm email" |
| Tables not found | Make sure you ran `schema.sql` in the SQL Editor |
| RLS blocking queries | Ensure you're logged in (authenticated). RLS policies only allow `authenticated` role |
| Charts not loading | Check browser console for errors. Make sure Chart.js CDN loaded |
| CORS errors | Supabase handles CORS automatically. If you see CORS errors, check your Supabase URL is correct |

---

## Architecture

```
Browser (HTML/CSS/JS)
    ↓ Supabase JS SDK (CDN)
Supabase
    ├── Auth (email/password)
    ├── PostgreSQL (tables + RLS)
    └── PostgREST (auto-generated API)

Hosted on: Netlify (static files)
Backend server: None ✨
```
