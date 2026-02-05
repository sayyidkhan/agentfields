# AgentField Hackathon - Idea Overview

All ideas follow the **Three Magi Pattern**: Multiple specialized agents with competing perspectives + Judge agent for context-aware arbitration.

---

## 💡 Idea 1: MagiStock
**Persona-aware investment decision system with three competing strategy agents (Fire/Water/Grass) and a judge that picks based on user risk tolerance.**

- **Category:** Finance / Investment
- **High-stakes decision:** Portfolio strategy selection
- **Judge considers:** Risk tolerance, time horizon, emotional sustainability
- **Prevents:** Abandoning good strategies during volatility

---

## 💼 Idea 2: TechHR-Magi
**Post-interview hiring advisory that analyzes candidates through technical skills, team fit, and growth potential to prevent hiring mistakes.**

- **Category:** HR / Talent Acquisition
- **High-stakes decision:** Tech hiring
- **Judge considers:** Team composition, role needs, diversity goals
- **Prevents:** Hiring for skills alone, missing culture fit

---

## 🚗 Idea 3: WheelMagi
**Car purchase advisor with Thrill/Practical/Future agents that prevents buyer's remorse by stress-testing actual usage vs stated preferences.**

- **Category:** Consumer / Automotive
- **High-stakes decision:** $30-50k purchase with 5-10 year impact
- **Judge considers:** Usage patterns, TCO, life stage, values alignment
- **Prevents:** Buying aspirational car that doesn't fit reality

---

## 💻 Idea 4: TechMagi
**Electronics buying assistant (Performance/Value/Simplicity agents) that matches devices to actual usage patterns and ecosystem compatibility.**

- **Category:** Consumer Electronics
- **High-stakes decision:** $500-3000 tech purchase
- **Judge considers:** Usage patterns, proficiency, ecosystem lock-in
- **Prevents:** Overpaying for unused features or switching ecosystem pain

---

## 📊 Idea 5: ToolMagi *(Bonus - Not Detailed Yet)*
**SaaS/software stack advisor with Integration/Simplicity/Cost agents for businesses choosing tools that fit team capability and scale.**

- **Category:** B2B / Software Procurement
- **High-stakes decision:** Multi-year software commitments
- **Judge considers:** Team size, technical capability, growth stage
- **Prevents:** Vendor lock-in and tool bloat

---

## 🏢 Idea 6: SupplyMagi *(Bonus - Not Detailed Yet)*
**B2B vendor selection system with Cost/Quality/Relationship agents for supply chain decisions considering risk tolerance.**

- **Category:** B2B / Procurement
- **High-stakes decision:** Supplier relationships
- **Judge considers:** Volume needs, quality requirements, supply chain risk
- **Prevents:** Optimizing for cost alone and quality failures

Great for removing bias from the executives or managers procuring the contract.

---

## 🎯 Recommended for Hackathon

**Top 3 Strongest Ideas:**

1. **TechHR-Magi** - Highest leverage (hiring mistakes cost 6-12 months salary), clear demo, judges will relate
2. **WheelMagi** - Strong emotional vs rational tension, relatable, TCO analysis impressive
3. **MagiStock** - Original concept, financial domain credibility, Tamagotchi growth angle unique

**Backup:**
- **TechMagi** - If consumer angle preferred, solid demo potential

---

## 🧠 Core Pattern: The Three Magi Framework

All ideas share:
- ✅ **3 specialized agents** with distinct perspectives
- ✅ **Self-critique** (agents acknowledge their bias)
- ✅ **Judge agent** that's context-aware, not just performance-optimizing
- ✅ **Persona alignment** (right for YOU, not just "best")
- ✅ **High-stakes decisions** (expensive mistakes, long time horizons)
- ✅ **Backend reasoning** (not chatbots)

---

## 📈 Alignment with Hackathon Criteria

| Criterion | All Ideas Score |
|-----------|----------------|
| **New problem space** | ✅ Decision engines, not chatbots |
| **Replaced complexity** | ✅ Eliminates consensus paralysis |
| **High leverage** | ✅ High-cost, high-regret domains |
| **Previously impossible** | ✅ Multi-agent reasoning with persona-awareness |

---

---

## 🏆 MY STRONG RECOMMENDATION: TechHR-Magi

### Why TechHR-Magi Wins the Hackathon

**1. Maximum Judge Appeal**
- **Every judge has hiring pain** - this is universally relatable
- B2B > B2C in perceived value
- Clear ROI story (hiring mistake = 6-12 months salary wasted)
- Judges will think "I need this on Monday"

**2. Perfect Demo Narrative**
- **Scenario:** Technical rockstar who's arrogant (Skills: Hire, Team: No, Growth: Hire)
- Judge decision makes or breaks team culture → **high drama**
- Easy to show multi-agent disagreement visually
- 3-minute demo writes itself

**3. Hackathon Criteria Alignment**
- ✅ **New problem space:** Not a chatbot - backend decision engine for HR
- ✅ **Replaced complexity:** Eliminates "let's meet again" consensus hell
- ✅ **High leverage:** Hiring mistakes cost $100k+ (salary + opportunity cost)
- ✅ **Previously impossible:** No tool does multi-dimensional candidate analysis with team context

**4. Technical Feasibility**
- **Simple data model** (JSON interview scores + notes)
- **No external APIs needed** (synthetic data is fine)
- **Clear agent separation** (technical skills vs culture vs growth)
- **Explainable AI** (transparency is the feature)

**5. Startup Potential Beyond Hackathon**
- ATS integration potential (Greenhouse, Lever)
- Interviewer bias detection (pattern analysis across interviews)
- Huge TAM (every company hires)
- Recurring revenue (per-hire or subscription)

---

## 🥈 Runner-Up: WheelMagi

**Why it's strong:**
- Emotional vs rational tension = compelling demo
- TCO analysis is impressive (most buyers ignore this)
- High regret domain (everyone knows someone who bought wrong car)

**Why it's second choice:**
- B2C perceived as lower value than B2B
- Requires real car data (more setup work)
- Judges may not relate as personally as hiring pain

---

## 🥉 Third Place: MagiStock

**Why it's good:**
- Your original concept (most polished)
- Tamagotchi growth angle is unique
- Financial domain = smart audience

**Why it's third choice:**
- Finance is crowded space (judges have seen many fintech demos)
- Investment advice = regulatory complexity vibes
- Harder to show immediate business impact vs TechHR-Magi

---

## ⚠️ Ideas to Avoid for Hackathon (Still Good Startup Ideas)

**ToolMagi** - Too broad, hard to demo impact in 3 minutes  
**SupplyMagi** - B2B but niche domain, judges may not relate  
**TechMagi** - B2C electronics less impressive than B2B hiring  

---

## 🎯 Final Verdict

**Go with TechHR-Magi if:** You want to win (maximize judge appeal + demo impact + technical feasibility)

**Go with WheelMagi if:** Your team is more excited about consumer products and you want something fun

**Go with MagiStock if:** You want to polish your original idea and you're passionate about finance

---

## 🚀 Next Steps (Assuming TechHR-Magi)

1. **Define 3-4 candidate profiles** (Technical Star/Culture Risk, Solid Mid-Level, Safe but Unremarkable)
2. **Create JSON interview data** (coding, system design, behavioral, culture rounds)
3. **Build agent reasoning** with AgentField framework
4. **Prepare demo script** showing agent disagreement → judge synthesis
5. **Practice pitch** emphasizing "backend AI decision engine, not chatbot"

### Demo Flow (3 minutes)
- **0:00-0:30** - Problem: "We hired for skills, he's brilliant but team hates him"
- **0:30-1:30** - Show 3 agents analyzing same candidate (disagreement!)
- **1:30-2:30** - Judge synthesizes with team context → final decision
- **2:30-3:00** - Impact: "This prevents $100k+ hiring mistakes"

---

**Last updated:** Feb 5, 2026  
**For:** AgentField Day Hackathon (Singapore)  
**Recommendation:** TechHR-Magi > WheelMagi > MagiStock
