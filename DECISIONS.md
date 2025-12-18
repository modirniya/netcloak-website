# NetCloak Business Decisions & Strategy

**Last Updated:** 2025-12-18

This document outlines key strategic decisions for the NetCloak wholesale VPN platform.

---

## Business Model Overview

**Three-Layer B2B Architecture:**
- **Platform (NetCloak)** → Sells wholesale VPN infrastructure to phone shops
- **Phone Shops** → Offer VPN subscriptions to their customers
- **Subscribers** → End-users who receive pre-configured VPN access

**Core Principle:** Platform provides infrastructure only. Phone shops own customer relationships, handle billing, and manage support.

---

## Target Customer: Mobile Phone Retail Shops

**Primary Market (MVP):** Philippines

**Shop Profile:**
- Established mobile phone retailers
- Sell 20-100+ phones per month
- Have existing customer base
- Already collect recurring payments (prepaid load, accessories)
- Looking for passive income streams

**Why Phone Shops:**
- Built-in distribution (sell phones = sell VPN bundles)
- Established customer relationships
- Already handle monthly collections
- Business verification possible (tax ID, permits, storefront)
- Predictable volumes (25-200+ subscribers per shop)
- Self-sufficient operations (minimal support burden)

---

## Pricing Structure

### Wholesale Pricing
- **$0.75/month per subscriber** (₱43 PHP in Philippines)
- 1 point = 1 day of service
- Points never expire (excluding promotional points)

### Cost Structure
- **Infrastructure cost:** $0.0239 per account/month (Contabo VPS 20)
- **Platform margin:** 96.8% ($0.7261 profit per subscriber)
- **Shop margin flexibility:** Can charge ₱99-149/month retail

### Economics Example (50 subscribers)
```
Shop pays:     ₱43/subscriber/month × 50 = ₱2,150/month
Shop charges:  ₱99/subscriber/month × 50 = ₱4,950/month
Shop profit:   ₱2,800/month passive income
```

### Rationale
- Affordable in low-income markets
- Simple flat pricing (no tiered complexity)
- High margin ensures platform sustainability
- Shops have 130-246% markup potential

---

## Philippines Market Analysis

### Why Philippines First

**Legal Environment:**
- VPNs fully legal with no restrictions
- Strong data protection framework
- No mandatory data retention for VPN providers
- No government censorship or blocking
- **Risk Level:** Very Low

**Economic Fit:**
- Average income: ₱44,800/month ($780 USD)
- Minimum wage: ₱19,000/month ($331 USD)
- Mobile spending: ₱300-500/month typical
- **VPN at ₱99-149 = 0.36-0.90% of monthly income**
- Extremely affordable even for minimum wage workers

**Market Characteristics:**
- 30% VPN adoption rate (high demand)
- Mobile-first population
- Strong phone retail shop ecosystem
- English-speaking (easier operations)
- Familiar with GCash/bank transfer payments
- Active remittance culture (payment infrastructure)

**Competitive Landscape:**
- Commercial VPNs charge ₱400-600/month
- NetCloak shops can charge ₱99-149 (50-75% cheaper)
- Differentiation: Local support, pre-configured, bundled with phone

### Target Cities (MVP)
- Metro Manila (primary)
- Cebu City
- Davao City
- Quezon City
- Makati

---

## Payment Processing Strategy

### Primary: Wise Business (B2B International Transfers)

**Why Wise:**
- ✅ B2B transfers (not VPN consumer payments = no classification risk)
- ✅ Low fees (0.43-0.69% vs 3-6% merchant accounts)
- ✅ Multi-currency support (PHP, USD, MXN, BRL, etc.)
- ✅ No monthly fees
- ✅ No account termination risk for VPN business
- ✅ Fast setup (1-3 days approval)

**How It Works:**
1. Phone shop transfers PHP to NetCloak Wise PHP account
2. Wise converts PHP → USD (0.43% fee)
3. NetCloak receives USD in Wise balance
4. NetCloak transfers USD to Novo bank account (free ACH)

**Cost Example:**
- Shop pays: ₱5,730 PHP ($100 USD worth of points)
- Wise fee: 0.43% = $0.43
- NetCloak receives: $99.57
- Transfer to Novo: $0 (free ACH)

### Secondary: GCash/PayMaya Business

**For shops preferring mobile payments:**
- GCash Business account (1-2% fees)
- Instant transfers
- 50M+ Filipino users
- Familiar payment method

### Backup: Bank Transfer / Remittance

**For unbanked shops:**
- Cash deposit at Palawan Pawnshop, Cebuana Lhuillier
- Direct bank transfer (InstaPay/PESONet)
- 2-5% fees but accessible anywhere

### NOT Using (For MVP)
- ❌ Merchant accounts (Stripe, PayPal, Durango)
  - Reason: Unnecessary for B2B wholesale model
  - Save 3-6% in fees
  - Avoid VPN classification risk
- ❌ Cryptocurrency (initially)
  - Reason: Too complex for small phone shops
  - Can add later as option

---

## Technical Specifications

### Service Tiers

**Fast Plan (MVP - Default):**
- **Speed:** Up to 15 Mbps
- **Data cap:** 5 GB per day (resets daily at midnight UTC)
- **Monthly equivalent:** ~150 GB/month if maxed daily
- **Device installations:** Up to 2 devices
- **Concurrent connections:** 1 device at a time
- **Platform support:** Mobile-only (Android/iOS)
- **Wholesale price:** $0.75/month
- **Suggested retail:** ₱99-149/month

**Premium Plan (Post-MVP):**
- **Speed:** Up to 40 Mbps
- **Data cap:** 15 GB per day (resets daily at midnight UTC)
- **Monthly equivalent:** ~450 GB/month if maxed daily
- **Device installations:** Up to 2 devices
- **Concurrent connections:** 1 device at a time
- **Platform support:** Mobile-only (Android/iOS)
- **Wholesale price:** $1.50/month
- **Suggested retail:** ₱199-249/month

### Why These Limits?

**Fast Plan - Speed (Up to 15 Mbps):**
- ✅ Fast enough for HD streaming (Netflix HD = 5 Mbps, YouTube 1080p = 5 Mbps)
- ✅ Smooth video calls and browsing
- ✅ Feels "premium" not "budget"
- ✅ Balances quality with infrastructure cost

**Fast Plan - Daily Cap (5 GB/day):**
- ✅ Generous for typical mobile usage (1-2 GB/day average)
- ✅ Prevents torrent abuse (can't download massive files)
- ✅ Daily reset feels generous (fresh start every day)
- ✅ Natural load balancing (prevents sustained heavy bandwidth usage)
- ✅ Better UX than monthly cap (no surprise "out of data" at month-end)

**Real-world usage covered (Fast Plan):**
- Browsing/social media all day: 500 MB/day ✅
- YouTube HD (4+ hours): 4 GB/day ✅
- Netflix HD (4+ hours): 4 GB/day ✅
- Music streaming (all day): 200 MB/day ✅
- Video calls (2+ hours): 1 GB/day ✅

**Single Concurrent Connection:**
- ✅ Prevents account sharing abuse
- ✅ Allows user to switch between phone/tablet
- ✅ Standard practice for consumer VPN services
- ✅ Reduces server load

### Infrastructure

**Fast Plan:**
- **VPN Protocol:** WireGuard + encrypted WebSockets
- **Application Stack:** Go-based (netcloak-edge, netcloak-engine)
- **Memory footprint:** <100MB RAM per application
- **Server capacity:** 200 accounts per VPS
- **Hosting:** Contabo Cloud VPS 20 ($4.77/month)
- **Port speed:** 300 Mbit/s
- **Specifications:** 6 vCPU cores, 12 GB RAM, 100 GB NVMe storage
- **Cost per user:** $4.77 ÷ 200 = $0.0239/user/month
- **Platform margin:** 96.8%

**Premium Plan (Future):**
- **Hosting:** Contabo Cloud VPS 30 ($12.00/month)
- **Port speed:** 600 Mbit/s
- **Server capacity:** 100 accounts per VPS (higher quality guarantee)
- **Cost per user:** $12.00 ÷ 100 = $0.12/user/month
- **Platform margin:** 92.0%

### Deferred Features (Post-MVP)

**Not in initial launch:**
- Premium tier (will add after validating Fast plan demand)

**Not Planned:**
- ❌ **Desktop support:** Never (mobile-only reduces abuse by 85%)
- ❌ **Unlimited data:** Never (prevents abuse, maintains quality)
- ❌ **Multiple concurrent connections:** Never (abuse prevention)

---

## Risk Mitigation Strategy

### Abuse Prevention

**Technical Controls:**
1. **Mobile-only approach** - Reduces abuse by ~85% vs desktop VPN
2. **No proxy hosting** - Feature disabled on smartphones
3. **Port blocking** - P2P ports, SMTP blocked
4. **Speed/bandwidth limits** - Deters heavy torrenting (5 Mbps/50GB)

**Business Controls:**
5. **Shop accountability** - Strike system for abuse from their subscribers
6. **Manual approval** - Every shop vetted before activation
7. **Business verification** - Tax ID, business permit, storefront photos required
8. **Subscriber limits** - Start with max 100 subscribers per shop

### Strike System

**If shop's subscribers generate abuse (DMCA, spam, attacks):**
- **Strike 1:** Warning + 7-day suspension
- **Strike 2:** 30-day suspension
- **Strike 3:** Permanent ban + no refund on remaining points

**Why this works:** Phone shops have physical storefronts, business licenses, and reputation to protect. Legal accountability exists.

### Legal Protection

1. **Business entity:** NeuEra Apps LLC (California)
2. **Legal documentation:** Budget $3,000-5,000 for:
   - Terms of Service
   - Privacy Policy
   - Partner Shop Agreement (with indemnification clauses)
3. **DMCA compliance:** Register DMCA agent ($6)
4. **Minimal logging:** Timestamps and bandwidth only (not browsing history)
5. **Insurance:** Recommended when profitable

### Growth Control (Crawl → Walk → Run)

- **Phase 1 (Month 1-3):** 10-20 shops in Metro Manila
- **Phase 2 (Month 4-6):** 50-75 shops across major Philippine cities
- **Phase 3 (Month 7-12):** 200-300 shops, expand to Cebu/Davao

**Always-waitlisted approach:** Prevents infrastructure overwhelm, allows policy refinement, maintains quality control.

---

## Shop Selection & Verification

### Application Requirements

**Business Information:**
- Business name and registration number
- Tax Identification Number (TIN)
- Business permit/DTI registration
- Physical storefront address
- Owner name and contact info
- Years in operation
- Monthly phone sales volume

**Verification Documents:**
- Business permit photo
- Valid ID of owner
- Storefront photo (exterior with signage)
- Facebook business page (if applicable)

### Approval Criteria (Objective)

**Auto-approve if:**
- ✅ Business registered for 1+ years
- ✅ Valid TIN and business permit
- ✅ Physical storefront verified
- ✅ Sells 20+ phones/month
- ✅ Owner ID verified
- ✅ Clean background (no fraud history)

**Auto-reject if:**
- ❌ Incomplete documentation
- ❌ Cannot verify physical location
- ❌ Business <6 months old
- ❌ Suspicious activity patterns

**Manual review if:**
- New business (<1 year) but strong documentation
- High volume shop (needs extra vetting)
- Unusual business structure

### Application Process (Simplified)

**Stage 1: Short Application (2-3 minutes)**
- Online form with business details
- Upload business permit + owner ID
- Storefront photo

**Stage 2: Verification (1-2 days)**
- Review documents
- Google Maps verification of storefront
- Facebook page check (if provided)
- Quick phone call (5-10 min) to confirm details

**Stage 3: Trial Access**
- Approved shops receive 300-900 trial points
- Can create 10-30 test accounts
- Try service before committing to purchase

---

## Marketing Strategy

### Target Market: Philippines Mobile Phone Shops

**Messaging Focus:** Recurring revenue opportunity (profit-driven, professional)

**Value Proposition:**
> "Add ₱2,800-4,000/month recurring revenue to your phone shop. Offer fast VPN service (up to 15 Mbps, 5 GB daily data) bundled with phone sales. We handle infrastructure, you keep the profits."

### Marketing Channels (Phase by Phase)

**Phase 1 (Month 1-3): Direct Outreach**
- Facebook Messenger to 100 Manila phone shops
- Google Maps search → email/call top shops
- Greenhills Shopping Center (electronics hub)
- Offer: Early access, generous trial (90 points free)

**Phase 2 (Month 4-6): Paid Ads**
- Facebook Ads (Philippines-targeted)
  - Audience: Business owners, 25-50, interested in "entrepreneurship" + "mobile phones"
  - Budget: $10-20/day
  - Creative: Simple profit calculation video
- Instagram/TikTok short-form content

**Phase 3 (Month 7-12): Partnerships**
- Wholesale phone distributors (reach 100s of shops)
- Prepaid load aggregators
- Phone accessories suppliers
- Trade associations

### Marketing Message Examples

**Headline (Filipino):**
"Mga Phone Shop Owners: Dagdag kita ng ₱2,800+/buwan"

**Headline (English):**
"Phone Shop Owners: Add ₱2,800-4,000/month Recurring Revenue"

**Body:**
```
Your shop already sells phones. Now earn passive monthly income
from every customer—zero inventory, no technical work.

Service Features:
✅ Fast: Up to 15 Mbps speed
✅ Generous: 5 GB daily data
✅ Quality: Perfect for streaming and browsing

Your Economics:
✅ Wholesale cost: ₱43/customer/month
✅ Retail price: ₱99-149/month
✅ Your profit: ₱56-106 per customer
✅ 50 customers = ₱2,800-5,300/month

Pre-configured. Pre-installed. They walk out with VPN ready.
You collect monthly. We handle infrastructure.

Limited spots. Apply today.
```

---

## Legal & Tax Structure

### Business Entity
- **Name:** NeuEra Apps LLC
- **Type:** Single-member LLC (California)
- **Tax Treatment:** Pass-through taxation (Schedule C)
- **Owner compensation:** Owner's draws

### Pre-Revenue Phase (Current)
- Track expenses in spreadsheet with receipts
- Pay from personal account temporarily
- Reimburse from business account when revenue starts

### Post-Revenue Tax Strategy
- Set aside 35-40% of profit for taxes
- Quarterly estimated tax payments
- Schedule C reporting
- Maintain clear separation of business/personal expenses

### Required Accounts
- **Novo:** Business checking ✅ (established)
- **Wise Business:** International payments ⏳ (setup this week)
- **GCash Business:** Philippine mobile payments ⏳ (optional, explore if accessible)

---

## Trial & Points System

### Shop Trial Access
- New shops receive 300-900 trial points (10-30 days)
- Can create test accounts for verification
- Builds confidence before financial commitment
- Reduces refund requests

### Points System
- 1 point = 1 day of service
- Points never expire (unless promotional)
- Decimal precision (e.g., 847.3 points)
- Always display one decimal place
- Validate sufficient balance before operations

### Bulk Point Packages (Suggested)
- 900 points (1 month) = ₱38,678 (~$675)
- 2,700 points (3 months) = ₱116,100 (~$2,025) - Save 5%
- 10,800 points (12 months) = ₱463,320 (~$8,100) - Save 10%

---

## Terminology

### Chosen Terms
- **"Phone Shop" / "Partner Shop"** - Clear, professional, describes actual customer
- **"Subscriber"** - End-user receiving VPN service
- **"Points"** - Wholesale currency (1 point = 1 day)

### Deprecated Terms
- ~~"Organizer"~~ - Too vague, mission-driven connotation
- ~~"Community Connector"~~ - Overly complex, added friction
- ~~"Retailer/Reseller"~~ - Technically accurate but less friendly

---

## Key Strategic Principles

1. **Phone shops only (MVP)** - No individual organizers initially
2. **Philippines first** - Validate model before expanding
3. **Wise Business primary** - Avoid merchant account drama
4. **Manual approval always** - Never automate shop acceptance
5. **Controlled growth** - Crawl → Walk → Run (resist scaling pressure)
6. **Mobile-only forever** - Never add desktop support (abuse prevention)
7. **Flat global pricing** - Keep wholesale at $0.75/month
8. **Profit-focused messaging** - Clear ROI, professional tone
9. **Business verification** - Objective criteria, not subjective vetting
10. **Trial before purchase** - Build trust, reduce friction

---

## Next Steps (Prioritized)

### This Week
1. ✅ Create Wise Business account (apply today)
2. ✅ Draft simple invoice template
3. ⏳ Research GCash Business requirements
4. ⏳ Create landing page (one-page, profit-focused)
5. ⏳ Draft short application form (business-only)

### Month 1 (January 2026)
1. Contact 50 Manila phone shops (Facebook/email/phone)
2. Onboard 5-10 beta shops with generous trial
3. Collect feedback on pricing, payment methods, process
4. Refine application and verification workflow
5. Document common questions for FAQ

### Month 2-3 (February-March 2026)
1. Scale to 20 shops total
2. Launch Facebook Ads (₱500-1,000/day budget)
3. Set up automated points management system
4. Draft legal documents (ToS, Privacy Policy, Shop Agreement)
5. Register DMCA agent

### Month 4-6 (April-June 2026)
1. Scale to 50-75 shops
2. Expand beyond Metro Manila (Cebu, Davao)
3. Add GCash Business payment option
4. Implement shop admin dashboard
5. Evaluate bulk pricing discounts

### Month 7-12 (July-December 2026)
1. Scale to 200-300 shops
2. Consider second market (Mexico or Brazil)
3. Evaluate high-risk merchant account (if needed for expansion)
4. Build mobile apps (Android/iOS)
5. Explore partnership with phone distributors

---

## Open Questions / Future Decisions

1. **Bulk pricing discounts?** Should 3-month/12-month purchases get discounts?
2. **Regional expansion timing?** When to add Mexico/Brazil?
3. **Subscriber cap per shop?** Start with 100 max, or unlimited from day 1?
4. **GCash vs Wise preference?** Which do shops prefer in practice?
5. **Marketing spend allocation?** Direct outreach vs paid ads ratio?
6. **Shop support model?** Self-service knowledge base or direct WhatsApp/Messenger support?
7. **Referral incentives?** Should shops earn bonus points for referring other shops?

---

## Market Expansion Roadmap (Post-Philippines Success)

### Green Zone Markets (Low Risk, Good Fit)

**Tier 1: Next After Philippines**
- **Mexico** - Legal, good purchasing power, large market
- **Brazil** - Legal, huge market, strong VPN demand

**Tier 2: Later Expansion**
- **Thailand** - Legal but monitor enforcement trends
- **Nigeria** - Legal but unpredictable regulatory environment

### Red Zone Markets (Avoid)
- ❌ **India** - 5-year data retention kills value proposition
- ❌ **Egypt** - Only government-approved VPNs legal
- ❌ **Vietnam** - Licensing requirements unclear for foreign operators
- ❌ **Indonesia** - High demand but restrictive government environment

---

*This document represents current strategy as of December 18, 2025. Model will evolve based on Philippines market validation results.*
