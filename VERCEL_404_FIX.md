# Fixing 404 Error on Vercel

## The Problem

Your MaScan app shows **404: NOT_FOUND** on Vercel because **DATABASE_URL environment variable is not set** in your Vercel project.

Without the database URL, Flask routes are not registered, causing every request to return 404.

## Quick Fix (5 minutes)

### Step 1: Get Your Supabase Connection String

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your `mascan-app` project
3. Click **Settings** → **Database**
4. Find **Connection string** section
5. Select **URI** tab
6. Copy the connection string (looks like: `postgresql://user:password@host:port/dbname`)

### Step 2: Add Environment Variables to Vercel

1. Go to [Vercel Dashboard](https://vercel.com)
2. Select your MaScan project
3. Click **Settings** → **Environment Variables**
4. Add these variables:

| Variable Name | Value | Example |
|--------------|-------|---------|
| `DATABASE_URL` | Your Supabase connection string | `postgresql://postgres:yourpassword@db.supabase.co:5432/postgres` |
| `SECRET_KEY` | Generate a random key | `openssl rand -hex 32` |
| `FLASK_ENV` | production | `production` |

### Step 3: Redeploy

1. In Vercel dashboard, click **Deployments** tab
2. Find your latest deployment
3. Click the three-dot menu → **Redeploy**
4. Wait for deployment to complete

### Step 4: Test

Visit your Vercel URL:
- `https://your-project.vercel.app/` - Should return app info
- `https://your-project.vercel.app/health` - Should return health status
- `https://your-project.vercel.app/setup-help` - If database still not connected, shows setup instructions

## What Changed

The app now has:

✅ **Basic routes** that work without database
- `/` - Health check
- `/health` - Detailed health status  
- `/setup-help` - Configuration guide

✅ **Better error messages** on Vercel
✅ **Automatic database setup** when DATABASE_URL is provided

## Detailed Steps (If Needed)

### Generate a Safe SECRET_KEY

```bash
# On Windows (PowerShell)
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes($bytes)
[Convert]::ToBase64String($bytes)

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Verify Supabase Connection String Format

Should look like:
```
postgresql://postgres:YOUR_PASSWORD@db.REGION.supabase.co:5432/postgres
```

⚠️ Replace `YOUR_PASSWORD` with your actual Supabase password!

## Common Issues

### Still Getting 404?

1. **Check Vercel logs:**
   - Vercel Dashboard → Deployments → Click deployment → View logs

2. **Verify environment variables:**
   - Settings → Environment Variables
   - Make sure DATABASE_URL is checked for "Production" environment

3. **Force redeploy:**
   - Delete the deployment and redeploy from GitHub

### Database Connection Fails?

1. Check DATABASE_URL format is correct
2. Verify Supabase project is running (not paused)
3. Check Supabase firewall settings
4. Try connecting from your local machine first

## Next Steps

Once deployment is working:

1. Log in with default credentials:
   - Username: `admin`
   - Password: `Admin@123`

2. **Change the admin password immediately!**

3. Start using the app!

## Need More Help?

- See **DEPLOYMENT.md** for full deployment guide
- See **SUPABASE_SETUP.md** for Supabase configuration
- Check Vercel logs for detailed error messages
