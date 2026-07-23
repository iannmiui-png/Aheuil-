# Deployment Guide

This project includes an automated GitHub Actions workflow (`.github/workflows/deploy.yml`) configured specifically for **GitHub Pages**.

---

## 🌐 Deploying to GitHub Pages

### Step 1: Enable GitHub Actions Source
1. Push this repository to GitHub.
2. Navigate to your repository on GitHub: **Settings** > **Pages**.
3. Under **Build and deployment** > **Source**, select **GitHub Actions**.

### Step 2: Trigger Deployment
- Whenever you push code to the `main` or `master` branch, GitHub Actions will automatically:
  1. Check TypeScript types (`npm run lint`).
  2. Build the production static bundle into `./dist` with relative paths (`base: './'`).
  3. Deploy the compiled web application directly to GitHub Pages (`https://<username>.github.io/<repository-name>/`).
- You can also manually trigger deployment anytime from the **Actions** tab by selecting **Deploy to GitHub Pages** and clicking **Run workflow**.

---

## 🛠️ Local Development & Testing

```bash
# Install dependencies
npm ci

# Build the application bundle locally
npm run build

# Preview built static site
npm run preview
```

---

## ☁️ Deploying to Other Static Hosting (Vercel / Netlify / Render)

1. Connect your GitHub repository to your hosting provider.
2. Set build settings:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

