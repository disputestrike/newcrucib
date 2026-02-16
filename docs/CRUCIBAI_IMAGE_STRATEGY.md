# CRUCIBAI IMAGE SOURCING & GENERATION STRATEGY
## How We'll Get High-Quality Visuals for "Inevitable AI" Rebrand

**Version:** 1.0  
**Status:** Implementation Guide  
**Date:** February 16, 2026

---

## OVERVIEW: THREE-TIER IMAGE SOURCING STRATEGY

We'll use a **hybrid approach** combining AI-generated images, professional stock photos, and custom assets to create a cohesive visual experience that matches Microsoft Edge's design quality.

---

## TIER 1: AI-GENERATED IMAGES (Premium, Customized)

**Use For:** Hero sections, emotional storytelling, unique brand moments  
**Quality:** Highest (custom-tailored to brand)  
**Cost:** Time investment (AI generation is included in Manus)  
**Quantity:** 4-6 hero images

### Images to Generate via AI

| # | Image | Purpose | Description | Placement |
|---|-------|---------|-------------|-----------|
| **1** | AI Code Generation Hero | Hero section visual | Futuristic visualization of code being generated in real-time, glowing terminals, holographic UI elements, clean modern aesthetic, dark background with blue/purple accents | Homepage hero (right side, 50/50 split) |
| **2** | Team Collaboration | Value prop visual | Diverse team of developers collaborating in modern office, screens showing code/design, collaborative energy, professional but creative | "What This Means for You" section |
| **3** | Developer Workflow | Use case visual | Developer at desk with VS Code open, CrucibAI interface showing, multiple screens, real-world context, productive energy | How It Works section |
| **4** | Enterprise Scale | Enterprise value prop | Large-scale visualization of distributed agents working together, network diagram aesthetic, infrastructure confidence, technical credibility | Architecture section |
| **5** | Speed & Certainty | Outcome visual | Abstract visualization of transformation: idea → reality, smooth flow, confident energy, modern design | Proof section |
| **6** | Future of AI | Evolution visual | Timeline-style visualization showing AI evolution (thinking → assisting → acting → guaranteeing), modern, sleek, forward-looking | Evolution section |

### Generation Parameters

**Style Guidelines:**
- **Aesthetic:** Modern, professional, futuristic but grounded
- **Color Palette:** Dark backgrounds with blue/purple/cyan accents (matches brand)
- **Quality:** 4K resolution, high detail, professional rendering
- **Tone:** Inspiring, confident, technical but accessible
- **Avoid:** Clichés (stock photo vibes), overly abstract, unrealistic

**Aspect Ratios:**
- Hero images: 16:9 (1920x1080 or 2560x1440)
- Section images: 4:3 or 16:9
- Grid images: 1:1 (square)

---

## TIER 2: PROFESSIONAL STOCK PHOTOS (Secondary, High-Quality)

**Use For:** Supporting visuals, use cases, real-world scenarios  
**Quality:** High (professional stock photography)  
**Cost:** Free (Unsplash, Pexels) or paid (Shutterstock)  
**Quantity:** 8-12 supporting images

### Stock Photos to Source

| # | Image | Purpose | Keywords | Placement |
|---|-------|---------|----------|-----------|
| **1** | Developer at Work | Use case | developer, coding, VS Code, laptop, focused | How It Works section |
| **2** | Team Meeting | Collaboration | team, meeting, startup, diverse, collaboration | Team/About section |
| **3** | Mobile Development | IDE Integration | mobile, development, IDE, programming | Features section |
| **4** | Office/Workspace | Enterprise | office, workspace, modern, professional | Enterprise value prop |
| **5** | Code Review | Quality | code review, team, quality, testing | Quality/Testing section |
| **6** | Deployment | Launch | deployment, servers, infrastructure, cloud | Deployment section |
| **7** | Success/Achievement | Outcome | success, achievement, celebration, milestone | Results section |
| **8** | Innovation | Future | innovation, technology, future, vision | Vision section |

**Where to Source:**
- **Unsplash** (free, high-quality): unsplash.com
- **Pexels** (free, diverse): pexels.com
- **Pixabay** (free, varied): pixabay.com
- **Shutterstock** (paid, premium): shutterstock.com

---

## TIER 3: CUSTOM ASSETS & ICONS (Branded, Functional)

**Use For:** Feature icons, diagrams, UI elements  
**Quality:** Medium (functional, branded)  
**Cost:** Time investment (design/creation)  
**Quantity:** 20-30 icons/diagrams

### Custom Assets to Create

| # | Asset | Purpose | Type | Placement |
|---|-------|---------|------|-----------|
| **1** | Agent Icons (115) | Feature showcase | Icon set | Features grid |
| **2** | Process Flow Diagram | How it works | Diagram | Process section |
| **3** | Architecture Diagram | Technical credibility | Diagram | Architecture section |
| **4** | Success Rate Badge | Proof | Icon/badge | Proof section |
| **5** | 72-Hour Timeline | Time to delivery | Icon/graphic | Timeline section |
| **6** | Transparency Visualization | Full visibility | Diagram | Transparency section |
| **7** | Category Evolution | Competitive positioning | Timeline/diagram | Evolution section |
| **8** | Pricing Icons | Pricing tiers | Icon set | Pricing section |

---

## IMPLEMENTATION PLAN

### PHASE 1: AI IMAGE GENERATION (Days 1-2)

**Step 1: Generate 6 Hero Images**

I'll use the Manus AI generation tool to create:
1. AI Code Generation Hero (homepage hero)
2. Team Collaboration (value props)
3. Developer Workflow (how it works)
4. Enterprise Scale (architecture)
5. Speed & Certainty (proof)
6. Future of AI (evolution)

**Process:**
- Write detailed, specific prompts for each image
- Generate at 4K resolution
- Review quality and alignment with brand
- Upload to CDN (Manus S3)
- Get public URLs for website integration

**Estimated Time:** 2-3 hours (including generation, review, upload)

**Output:** 6 high-quality hero images with CDN URLs

---

### PHASE 2: STOCK PHOTO SOURCING (Days 2-3)

**Step 1: Search & Curate Stock Photos**

I'll search Unsplash, Pexels, and Pixabay for:
- Developer/coding images
- Team collaboration images
- Office/workspace images
- Technology/innovation images

**Process:**
- Search using keywords from the table above
- Download high-resolution versions (2K+)
- Review for brand alignment (modern, professional, diverse)
- Organize by section/purpose
- Upload to CDN
- Get public URLs

**Estimated Time:** 3-4 hours (including search, curation, download, upload)

**Output:** 8-12 professional stock photos with CDN URLs

---

### PHASE 3: CUSTOM ASSETS & ICONS (Days 3-4)

**Step 1: Create Icon Sets**

I'll create:
- 115 agent category icons (frontend, backend, database, security, testing, deployment)
- Process flow diagrams
- Architecture diagrams
- Timeline graphics
- Badge/proof graphics

**Process:**
- Design using consistent style (matches brand)
- Create as SVG (scalable, lightweight)
- Optimize for web
- Integrate into website components

**Estimated Time:** 4-5 hours (including design, optimization, integration)

**Output:** 20-30 custom icons and diagrams

---

## IMAGE INTEGRATION INTO WEBSITE

### Homepage Hero Section

```html
<!-- 50/50 Split Layout -->
<section className="hero-section">
  <div className="hero-text">
    <h1>Inevitable AI</h1>
    <p>Intelligence that doesn't just act...</p>
    <button>Make It Inevitable</button>
  </div>
  <div className="hero-image">
    <img 
      src="https://cdn.manus.computer/crucibai/hero-ai-code-generation.png"
      alt="AI Code Generation"
    />
  </div>
</section>
```

### Features Section (Grid Layout)

```html
<!-- Feature Grid with Icons -->
<section className="features-grid">
  <h2>115 Specialized Agents</h2>
  <div className="grid-3x3">
    {agents.map(agent => (
      <div className="feature-card">
        <img src={agent.iconUrl} alt={agent.name} />
        <h3>{agent.name}</h3>
        <p>{agent.description}</p>
      </div>
    ))}
  </div>
</section>
```

### Value Propositions Section (Alternating Layout)

```html
<!-- Text Left, Image Right -->
<section className="value-prop">
  <div className="text-content">
    <h2>Solo Developers</h2>
    <p>Your idea → Deployed app (72 hours, not 6 months)</p>
  </div>
  <div className="image-content">
    <img 
      src="https://cdn.manus.computer/crucibai/developer-workflow.png"
      alt="Developer Workflow"
    />
  </div>
</section>
```

---

## CDN UPLOAD STRATEGY

### How Images Get to the Website

**Step 1: Generate/Source Images Locally**
- Create images on Manus sandbox
- Store in `/home/ubuntu/webdev-static-assets/`

**Step 2: Upload to Manus S3 CDN**
- Use `manus-upload-file` command
- Get public CDN URL (e.g., `https://cdn.manus.computer/crucibai/hero-1.png`)

**Step 3: Reference in Website Code**
- Use CDN URLs in HTML/React components
- Never store images in project directory (causes deployment bloat)

**Step 4: Deploy Website**
- Website references CDN URLs
- Images load from global CDN (fast, reliable)
- No local image files in deployment

### Example Upload Process

```bash
# Upload multiple images at once
manus-upload-file \
  /home/ubuntu/webdev-static-assets/hero-ai-code.png \
  /home/ubuntu/webdev-static-assets/team-collaboration.png \
  /home/ubuntu/webdev-static-assets/developer-workflow.png

# Returns:
# https://cdn.manus.computer/crucibai/hero-ai-code.png
# https://cdn.manus.computer/crucibai/team-collaboration.png
# https://cdn.manus.computer/crucibai/developer-workflow.png
```

---

## IMAGE QUALITY CHECKLIST

**Before Using Any Image, Verify:**

- [ ] **Resolution:** At least 1920x1080 (4K preferred for hero images)
- [ ] **Brand Alignment:** Matches dark theme, modern aesthetic, professional tone
- [ ] **Contrast:** Text readable if overlaid, images pop against background
- [ ] **Diversity:** Represents diverse teams, inclusive imagery
- [ ] **Relevance:** Directly supports messaging and section content
- [ ] **Optimization:** Compressed for web (< 500KB per image)
- [ ] **Accessibility:** Has descriptive alt text
- [ ] **Legal:** Licensed for commercial use (CC0, Unsplash, or purchased)

---

## TIMELINE

| Phase | Task | Duration | Days |
|-------|------|----------|------|
| **1** | AI Image Generation (6 hero images) | 2-3 hours | Day 1-2 |
| **2** | Stock Photo Sourcing (8-12 images) | 3-4 hours | Day 2-3 |
| **3** | Custom Icons & Diagrams (20-30 assets) | 4-5 hours | Day 3-4 |
| **4** | Website Integration | 3-4 hours | Day 4-5 |
| **5** | QA & Optimization | 2-3 hours | Day 5 |
| **Total** | All image work | 14-19 hours | 5 days |

---

## COST BREAKDOWN

| Source | Quantity | Cost | Notes |
|--------|----------|------|-------|
| **AI Generation** | 6 images | Included (Manus) | Premium, customized |
| **Stock Photos** | 8-12 images | Free (Unsplash/Pexels) | High quality, diverse |
| **Custom Icons** | 20-30 assets | Included (design time) | Branded, functional |
| **CDN Upload** | All images | Included (Manus) | Global delivery |
| **Total** | 34-48 assets | **$0** | All included in Manus |

---

## SUCCESS METRICS

**After images are integrated, measure:**

- [ ] Page load time (should be < 3 seconds with optimized images)
- [ ] Visual engagement (scroll depth, time on page)
- [ ] Brand consistency (all images align with "Inevitable AI" aesthetic)
- [ ] Conversion rate (CTA clicks, signups)
- [ ] Mobile responsiveness (images render correctly on all devices)
- [ ] Accessibility (alt text present, high contrast)

---

## NEXT STEPS

**Once you approve this image strategy:**

1. ✅ Generate 6 AI hero images (specific prompts ready)
2. ✅ Source 8-12 stock photos (keywords identified)
3. ✅ Create 20-30 custom icons/diagrams (design specs ready)
4. ✅ Upload all to CDN (URLs ready for website)
5. ✅ Integrate into website components (code ready)
6. ✅ Test and optimize (QA checklist ready)

**Ready to proceed?** 🚀

---

*Image Strategy Document | Version 1.0 | Status: Ready for Implementation*
