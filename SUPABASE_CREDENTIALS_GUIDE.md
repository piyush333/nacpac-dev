# Getting Supabase Credentials

Complete guide to create a Supabase project and extract the credentials needed for the agentic system.

---

## Step 1: Create Supabase Account (if needed)

1. Go to https://supabase.com/sign-up
2. Sign up with:
   - Email
   - GitHub (recommended, easier)
   - Google
3. Verify email

---

## Step 2: Create New Project

1. Go to https://supabase.com/dashboard
2. Click **New Project**
3. Fill in:
   - **Project name:** `jico-agentic` (or your choice)
   - **Database password:** Strong password (e.g., `KjX@9pLm2nV5qR#`)
   - **Region:** Select closest to you (e.g., `ap-south-1` for India)
4. Click **Create new project**
5. Wait 2-3 minutes for project to be created

You'll see a loading screen:
```
Setting up your new project...
This may take a few minutes.
```

---

## Step 3: Get SUPABASE_URL

Once project is created:

1. In the left sidebar, click **Settings** (gear icon)
2. Click **API** (under "Configuration")
3. Under **Project URL**, you'll see:
   ```
   https://your-project-id.supabase.co
   ```
4. Copy this entire URL

**In your .env file:**
```
SUPABASE_URL=https://your-project-id.supabase.co
```

---

## Step 4: Get SUPABASE_KEY (Anon Key)

Same **Settings → API** page:

1. Look for **API Keys** section
2. You'll see two keys:
   - **Anon Key** (public, safe to share)
   - **Service Role Key** (secret, keep private)

3. Copy the **Anon Key** (it starts with `eyJhbGc...`)

**In your .env file:**
```
SUPABASE_KEY=eyJhbGc... (the entire anon key)
```

---

## Step 5: Verify You Have Both

Your `.env` should now have:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (long string)
```

✅ Both should be non-empty

---

## Step 6: Create Tables (Run Schema)

Now you have the credentials, set up the database:

1. In Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **New Query**
3. Copy entire contents of `agentic/schema.sql` from your repo
4. Paste into the editor
5. Click **Run** (blue button)
6. Wait for "Success" message

You should see:
```
Query OK
[11 rows affected]
```

---

## Step 7: Verify Tables Were Created

1. In left sidebar, click **Tables**
2. You should see these tables:
   - `brands`
   - `tasks`
   - `runs`
   - `brand_state`
   - `builds`
   - `deployments`
   - `decisions`
   - `knowledge`
   - `costs`
   - `sessions`
   - `failed_tasks`

If you see all 11 tables, ✅ schema setup is complete!

---

## Troubleshooting

### "I can't find Settings → API"
- In Supabase dashboard, look at bottom left
- Click your project name → **Settings**
- On the settings page, click **API** in the left menu

### "I don't see the Anon Key"
- Make sure you're on **Settings → API** page
- Scroll down if needed
- Under "API Keys" section, click **Reveal** if key is hidden

### "Schema.sql failed to run"
- Check that you copied the ENTIRE file
- Make sure no lines are missing
- Try running in smaller chunks:
  - First, tables only
  - Then, views separately
  - Then, RLS policies separately

### "SUPABASE_URL is wrong"
- Should look like: `https://xxx-xxx-xxx.supabase.co`
- Should NOT include `/rest/v1` or trailing slashes
- Should NOT be the API URL (that's different)

### "SUPABASE_KEY is wrong"
- Should be 200+ characters long
- Should start with `eyJhbGc` or `eyJ0eXA`
- Should NOT include spaces
- Copy the entire key without truncating

---

## Quick Copy-Paste Template

Once you have credentials, fill this in:

```
# From Supabase Settings → API → Project URL
SUPABASE_URL=https://your-project-id.supabase.co

# From Supabase Settings → API → Anon Key
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Rest of your config...
ANTHROPIC_API_KEY=...
DISCORD_TOKEN=...
```

---

## Testing the Connection

Once you have credentials and schema is created, test:

```bash
cd agentic

# Copy .env template and fill in Supabase credentials
cp .env.template .env
nano .env

# Create Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test connection
python3 -c "
from memory import memory
state = memory.get_brand_state('nacpac')
print('✅ Supabase connected!')
print(f'  NacPac branch: {state[\"current_branch\"]}')
"
```

Expected output:
```
✅ Supabase connected!
  NacPac branch: develop
```

---

## Visual Walkthrough

### Location: Supabase Dashboard

```
Supabase Dashboard
├── Projects
│   └── [jico-agentic]
│       ├── SQL Editor ← Run schema.sql here
│       ├── Tables ← Verify tables created here
│       ├── Settings (gear icon)
│       │   └── API
│       │       ├── Project URL ← COPY THIS
│       │       └── API Keys
│       │           ├── Anon Key ← COPY THIS
│       │           └── Service Role Key (keep secret)
```

---

## Cost

Supabase free tier includes:
- ✅ 500MB storage
- ✅ 2GB bandwidth/month
- ✅ Real-time updates
- ✅ Unlimited API requests
- ❌ Unlimited users (but free tier has rate limits)

**For our use case:** Free tier is more than enough for the first 3+ months.

---

## Summary

| What | Where | Example |
|------|-------|---------|
| SUPABASE_URL | Settings → API → Project URL | `https://jico-agentic-abc123.supabase.co` |
| SUPABASE_KEY | Settings → API → Anon Key | `eyJhbGciOiJIUz...` (200+ chars) |

Once you have both, you're ready for deployment! ✅
