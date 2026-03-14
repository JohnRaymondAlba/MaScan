# MaScan Vercel + Supabase Deployment Guide

Complete guide to deploy MaScan on Vercel with Supabase database.

## Prerequisites

- GitHub account
- Vercel account (free tier)
- Supabase account (free tier) 
- Git installed

## 🚀 Quick Start (5 minutes)

### 1. Prepare Your Repository

```bash
# Clone your project or navigate to it
cd c:\Users\Asus\Downloads\MaScan

# Initialize git if not already done
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
# (Follow GitHub's instructions to create repo and add remote)
git remote add origin https://github.com/YOUR_USERNAME/mascan.git
git branch -M main
git push -u origin main
```

### 2. Create Supabase Project (2 minutes)

1. Visit [supabase.com](https://supabase.com) → Sign up
2. Create new project:
   - Name: `mascan-app`
   - Password: Generate strong password (save it!)
   - Region: Closest to you
   - Click **"Create"**

3. Wait for project to initialize (~1 minute)

4. Get connection string:
   - Click **"Settings"** → **"Database"**
   - Copy **PostgreSQL connection string**
   - **Replace `[YOUR-PASSWORD]` with your actual password**

Example:
```
postgresql://postgres:MyPassword123@db.xxx.supabase.co:5432/postgres
```

### 3. Create Vercel Project (1 minute)

1. Visit [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New"** → **"Project"**
3. Select **"Import Git Repository"**
4. Find and select your GitHub `mascan` repository
5. Click **"Import"**

### 4. Add Environment Variables (1 minute)

In Vercel project settings:

1. Go to **"Settings"** → **"Environment Variables"**

2. Add these 4 variables:

| Name | Value | Environments |
|------|-------|--------------|
| `DATABASE_URL` | Your Supabase connection string | All |
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` | All |
| `FLASK_ENV` | `production` | Production only |
| `REDIS_URL` | Your Redis URL (from Upstash) | Production only |

3. Click **"Save"**

### 5. Deploy (1 minute)

1. Back to project dashboard
2. Click **"Deployments"**
3. Your app should already be building!
4. Wait for it to finish (~2-3 minutes)

### 6. Verify Deployment

1. Click the deployment URL
2. Visit `https://your-app.vercel.app/health`
3. Should see `{"status": "ok"}`

✅ **You're live!** 🎉

---

## 📋 Complete Configuration Checklist

- [ ] GitHub repository created and pushed
- [ ] Supabase project created
- [ ] PostgreSQL connection string copied and password replaced
- [ ] Vercel project imported from GitHub
- [ ] Environment variables added to Vercel
- [ ] Deployment successful
- [ ] `/health` endpoint returns 200 OK
- [ ] Admin user created (auto-created, password: `Admin@123`)
- [ ] Changed admin password after first login

---

## 🔑 Getting Your Redis URL (Optional but Recommended)

Sessions will work without Redis, but it's recommended for production.

### Option A: Upstash (Free 10K commands/day)

1. Visit [upstash.com](https://upstash.com)
2. Sign up (GitHub recommended)
3. Click **"Create Database"**
4. Choose **"Redis"** and free tier
5. Create and copy the URL starting with `redis://`
6. Add to Vercel as `REDIS_URL`

### Option B: Redis Cloud (Free tier)

1. Visit [redis.com/try-free](https://redis.com/try-free)
2. Sign up
3. Create database
4. Copy endpoint URL
5. Add to Vercel as `REDIS_URL`

---

## 🔄 Updating Your App

Any time you push to `main` branch, Vercel auto-deploys:

```bash
# Make changes
git add .
git commit -m "Your message"
git push origin main

# Vercel automatically deploys within 1 minute
```

Check deployment status in Vercel dashboard under **"Deployments"**.

---

## 🛠️ Troubleshooting

### "INTERNAL_SERVER_ERROR" on first deployment

This is normal - tables are being created. Wait 30 seconds and refresh.

### "Database connection failed"

1. Check `DATABASE_URL` is correct in Vercel settings
2. Verify password is replaced in connection string
3. Check Vercel logs: **Deployments** → deployment → **"Runtime Logs"**

### Tables not showing in Supabase

1. Go to Supabase → **"SQL Editor"**
2. Wait 2-3 minutes after first deployment
3. Run: `SELECT * FROM information_schema.tables WHERE table_schema = 'public';`

### Admin login not working

- Username: `admin`
- Password: `Admin@123`
- Change after first login!

### Sessions not persisting

- Add `REDIS_URL` to environment variables
- Redeploy after adding it

---

## 📊 Database Schema

Automatically created tables:

- `events` - Event information
- `users` - User accounts (admin/scanner roles)
- `attendance` - Attendance records
- `attendance_timeslots` - Multi-slot attendance tracking
- `students_qrcodes` - Student QR code data
- `login_history` - User login/logout records
- `scan_history` - QR code scan records
- `activity_log` - System activity tracking

---

## 🔒 Security Checklist

✅ Use strong passwords
✅ Keep connection strings secret
✅ Don't commit `.env` files
✅ Change default admin password
✅ Use environment variables (never hardcode secrets)
✅ Enable Supabase row-level security if needed
✅ Backup your database regularly

---

## 📞 Support Resources

- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Flask Docs: https://flask.palletsprojects.com
- SQLAlchemy: https://www.sqlalchemy.org

---

## 🎯 Next Steps

After successful deployment:

1. **Change admin password**
   - Login with `admin` / `Admin@123`
   - Update password in settings

2. **Configure your settings**
   - Add events
   - Create scanner accounts
   - Upload student QR codes

3. **Monitor your app**
   - Check Vercel analytics
   - Review Supabase database metrics
   - Test QR code scanning

4. **Backup your data**
   - Use Supabase's backup feature
   - Export data regularly

---

## 💡 Performance Tips

- Database queries auto-optimize with PostgreSQL
- Use Vercel's edge functions for faster response times
- Add Cloudflare CDN for static assets
- Monitor database connections in Supabase dashboard

**Enjoy your live MaScan app!** 🚀🎓
