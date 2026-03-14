# Supabase Setup Guide for MaScan

This guide will help you set up Supabase (PostgreSQL) for your MaScan app on Vercel.

## Step 1: Create Supabase Account & Database

1. Go to [supabase.com](https://supabase.com)
2. Sign up for free (GitHub account recommended)
3. Create a new project:
   - Click "New project"
   - Choose a name (e.g., "mascan-app")
   - Create a strong database password (save it!)
   - Select region closest to you
   - Click "Create new project"

## Step 2: Get Your Connection String

1. In Supabase dashboard, go to **"Settings"** → **"Database"**
2. Find the **"Connection string"** section
3. Copy the **PostgreSQL connection string** (starts with `postgresql://`)
4. **Important**: Replace `[YOUR-PASSWORD]` with the password you created earlier

Example:
```
postgresql://postgres:YOUR_PASSWORD@db.example.supabase.co:5432/postgres
```

## Step 3: Configure Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Go to **"Settings"** → **"Environment Variables"**
3. Add these three variables:

**Variable 1: DATABASE_URL**
- Key: `DATABASE_URL`
- Value: Your PostgreSQL connection string from Step 2
- Environments: Production, Preview, Development (select all)

**Variable 2: SECRET_KEY**
- Key: `SECRET_KEY`
- Value: Generate a random string (e.g., `python -c "import secrets; print(secrets.token_hex(32))"`)
- Environments: All

**Variable 3: FLASK_ENV**
- Key: `FLASK_ENV`
- Value: `production`
- Environments: Production, Preview

**Variable 4: REDIS_URL** (Optional but recommended for sessions)
- Key: `REDIS_URL`
- Value: Your Redis URL (from Upstash or similar)
- Environments: Production

## Step 4: Deploy

1. Push your changes to Git:
   ```bash
   git add .
   git commit -m "Add Supabase configuration"
   git push
   ```

2. Vercel will automatically deploy
3. Check your deployment at `https://your-project.vercel.app/health`

## Step 5: Verify Tables Created

1. In Supabase, go to **"SQL Editor"**
2. Run this query to verify tables exist:
   ```sql
   SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
   ```

3. You should see: `events`, `users`, `attendance`, `activity_log`, `login_history`, `scan_history`, `students_qrcodes`, `attendance_timeslots`

## Troubleshooting

### Connection Error
- Check that `[YOUR-PASSWORD]` is replaced in the connection string
- Verify the password matches what you set in Supabase
- Ensure your IP is not blocked (Supabase allows all IPs by default)

### Tables Not Created
- Check Vercel deployment logs: **"Deployments"** → click deployment → **"Runtime Logs"**
- The tables are auto-created on first run

### Admin User Not Created
- First deployment auto-creates admin user: `username: admin`, `password: Admin@123`
- Change this password after first login!

## Local Development

To run locally with Supabase:

1. Create `.env` file in `/app` directory:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/postgres
   SECRET_KEY=your-secret-key
   FLASK_ENV=development
   REDIS_URL=redis://localhost:6379
   ```

2. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run locally:
   ```bash
   python app.py
   ```

Or to use SQLite locally (no .env needed):
```bash
python app.py
```
The app will default to SQLite if no `DATABASE_URL` is set.

## Security Tips

✅ **Do:**
- Use strong passwords for Supabase
- Change the default admin password immediately after setup
- Keep your connection string secret (never commit it)
- Use environment variables (never hardcode secrets)
- Enable Row Level Security (RLS) in Supabase if needed

❌ **Don't:**
- Share your Database URL
- Commit `.env` files to Git
- Use simple passwords
- Expose your admin credentials

## Backup & Recovery

To backup your Supabase database:

1. Go to Supabase dashboard
2. Click **"Start"** on the Backup section
3. Under **"Manual backups"**, click **"Back up now"**
4. Download backups from the **"Backups"** page

## Support

- Supabase Docs: https://supabase.com/docs
- MaScan Issues: Create an issue in your GitHub repo
