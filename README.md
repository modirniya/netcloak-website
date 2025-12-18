# NetCloak Website

Under construction page for NetCloak hosted on GitHub Pages.

## Setup Instructions

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit: Under construction page"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/netcloak-website.git
git push -u origin main
```

### 2. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on **Settings**
3. Navigate to **Pages** in the left sidebar
4. Under **Source**, select **Deploy from a branch**
5. Select **main** branch and **/ (root)** folder
6. Click **Save**

### 3. Configure Custom Domain (DNS Settings)

You need to configure DNS records with your domain registrar for `netcloak.app`:

#### Option A: Apex Domain (netcloak.app)
Add the following **A records**:
```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

#### Option B: WWW Subdomain (www.netcloak.app)
Add a **CNAME record**:
```
www.netcloak.app  →  YOUR_USERNAME.github.io
```

#### Recommended: Both
Set up both apex domain and www subdomain:
- Add all four A records for the apex domain
- Add a CNAME record for www pointing to your GitHub Pages URL

### 4. Verify Custom Domain in GitHub

1. Go to repository **Settings** → **Pages**
2. Under **Custom domain**, enter: `netcloak.app`
3. Click **Save**
4. Wait for DNS check to complete
5. Enable **Enforce HTTPS** once DNS is verified

### 5. DNS Propagation

DNS changes can take up to 48 hours to propagate, but usually complete within a few hours.

You can check DNS propagation status at: https://www.whatsmydns.net/

## Local Development

To preview locally, simply open `index.html` in your web browser, or use a local server:

```bash
python3 -m http.server 8000
```

Then visit: http://localhost:8000

## Files

- `index.html` - Main HTML page
- `style.css` - Styles and animations
- `CNAME` - Custom domain configuration for GitHub Pages
- `favicon.png` / `netcloak-icon.png` - App icon and favicon
- `DECISIONS.md` - Business strategy and decisions documentation
- `README.md` - This file

## Business Documentation

See `DECISIONS.md` for the complete NetCloak business strategy, including:
- Target market (Philippines mobile phone shops)
- Pricing structure ($0.75 wholesale, ₱99-149 retail)
- Payment processing (Wise Business)
- Risk mitigation and abuse prevention
- Growth roadmap and next steps
