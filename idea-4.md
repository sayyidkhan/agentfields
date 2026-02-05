# PRD: TechMagi – Intelligent Electronics & Gadget Buying Assistant

## 1. Problem Statement

Consumer electronics purchases are increasingly complex and regret-prone:
- **Spec overload** (do you need 16GB or 32GB RAM? 120Hz or 60Hz?)
- **Marketing manipulation** (flagship vs mid-range, last-gen vs new)
- **Ecosystem lock-in** (iPhone user considering Android, or vice versa)
- **Use case misalignment** (bought gaming laptop, mostly uses Excel and email)

Most tech recommendation tools optimize for:
- Best specs at price point
- Highest benchmark scores
- Latest features

They ignore:
- Your actual usage patterns
- Ecosystem compatibility
- Future-proofing vs overkill
- Total cost including accessories, subscriptions, upgradeability

Result: Buyers either overpay for features they don't use, or underbuy and hit limitations.

---

## 2. Proposed Solution

**TechMagi** is a persona-aware electronics buying advisory system.

Three specialized agents analyze devices through different lenses:
- **Performance Agent** (Power User): Specs, future-proofing, bleeding edge
- **Value Agent** (Pragmatist): Best bang-for-buck, refurbished, deals
- **Simplicity Agent** (Minimalist): Ease of use, ecosystem fit, just-enough features

A **Judge Agent** selects the best fit based on:
- Actual usage patterns (not stated needs)
- Technical proficiency
- Existing ecosystem (devices, subscriptions, workflows)
- Budget reality (including hidden costs)

---

## 3. System Overview

### 3.1 Core Agents

#### ⚡ Performance Agent (Power User / Future-Proof)
- **Focus:** Maximum performance, future-proofing, flagship features
- **Optimizes for:** Speed, capability, longevity, no compromises
- **Recommends:**
  - Latest generation processors
  - Maximum RAM and storage
  - High refresh rate displays
  - Latest connectivity standards
- **Bias:** Overestimates need for high-end specs

#### 💰 Value Agent (Pragmatist / Cost-Optimizer)
- **Focus:** Best value per dollar, smart compromises
- **Optimizes for:** Cost efficiency, deals, refurbished options
- **Recommends:**
  - Last-gen flagship (80% performance, 50% price)
  - Mid-range with excellent reviews
  - Refurbished/open-box deals
  - Accessories from third-party brands
- **Bias:** May sacrifice user experience for savings

#### 🎯 Simplicity Agent (Minimalist / Ease-of-Use)
- **Focus:** User experience, ecosystem integration, minimal complexity
- **Optimizes for:** Just-enough features, seamless integration, low friction
- **Recommends:**
  - Ecosystem-native devices (Apple for Apple users)
  - All-in-one solutions vs modular setups
  - Fewer features but better UX
  - Built-in vs requiring accessories
- **Bias:** May recommend more expensive ecosystem choices

---

### 3.2 Agent Analysis Process

Each agent:
1. **Ingests user profile:**
   - Current devices and ecosystem
   - Stated use cases
   - Budget and priorities
   - Technical proficiency

2. **Analyzes device options:**
   - Scores based on their priority lens
   - Identifies must-have vs nice-to-have features
   - Projects satisfaction over 2-3 year lifecycle

3. **Generates recommendation:**
   - Top 1-2 device choices with reasoning
   - Trade-offs and limitations
   - Total cost including accessories
   - Self-critique of own bias

---

### 3.3 Judge Agent (Reality-Check Arbiter)

The Judge Agent:
- **Reviews all three recommendations**
- **Applies reality filters:**
  - **Usage analysis:** What do you actually do vs what you say you need?
  - **Proficiency check:** Can you utilize pro features or will they go unused?
  - **Ecosystem penalty:** Switching ecosystems has friction costs
  - **Budget reality:** Total cost including hidden expenses
  - **Upgrade cycle:** How often do you actually upgrade?

- **Selects final recommendation:**
  - Best fit for actual behavior
  - Balances performance and value
  - Minimizes buyer's remorse
  - Explains why other options don't fit

---

## 4. Input Data Model (PoC Scope)

### User Profile
```json
{
  "purchase_intent": {
    "category": "laptop",
    "budget_max": 2000,
    "budget_preferred": 1500,
    "urgency": "medium"
  },
  "usage_patterns": {
    "primary_use": ["web_browsing", "coding", "video_calls"],
    "secondary_use": ["photo_editing", "occasional_gaming"],
    "hours_per_day": 8,
    "mobility": "daily_commute"
  },
  "current_ecosystem": {
    "phone": "iPhone 13",
    "tablet": "iPad Air",
    "subscriptions": ["iCloud", "Apple Music"],
    "accessories": ["AirPods Pro"]
  },
  "tech_proficiency": "intermediate",
  "upgrade_frequency": "3-4 years",
  "priorities": ["battery_life", "performance", "portability"]
}
```

### Device Database (Simplified for PoC)
- 15-20 representative devices in category
- Data: specs, price, reviews, ecosystem compatibility

---

## 5. Hackathon PoC Implementation

### 5.1 Scope Constraints
- **Single category** (e.g., Laptops)
- **Pre-defined device dataset** (15-20 options)
- **Synthetic user profiles** (3-4 personas)
- **No real-time pricing** (static data)

---

### 5.2 Technical Architecture

```
User Profile + Current Ecosystem
        ↓
  Device Database
        ↓
+--------------------------------------+
| Performance | Value | Simplicity    |
+--------------------------------------+
        ↓
  Analysis + Trade-off Mapping
        ↓
   Judge Agent
   (Reality-Check)
        ↓
  Final Recommendation
  + Total Cost + Reasoning
```

---

### 5.3 Technology Stack (Suggested)
- **Python** (AgentField framework)
- **JSON** for device specs and user profiles
- **LLM for:**
  - Agent reasoning and trade-off analysis
  - Ecosystem compatibility assessment
  - Judge synthesis and explanation
  - Use case matching

---

## 6. Success Criteria (Hackathon)

- **Clear agent disagreement** (Performance picks M4 Max, Value picks M3 Air refurb)
- **Judge explains ecosystem penalty** (if switching platforms)
- **Total cost comparison** (device + accessories + subscriptions)
- **Use case reality check** ("You say gaming, but you mostly code")
- **Handles different personas** (student vs professional vs creative)

---

## 7. Demo Scenarios

### Scenario 1: The Developer Who Doesn't Need Pro Hardware
- **User:** Software engineer, mostly web dev, says wants "powerful machine"
- **Performance Agent:** MacBook Pro M4 Max ($3500) - future-proof!
- **Value Agent:** MacBook Air M2 refurb ($899) - more than enough
- **Simplicity Agent:** MacBook Air M3 ($1099) - ecosystem fit, quiet, light
- **Judge:** "Your use case doesn't need Pro. Air M3 is 90% as good for 65% less."

### Scenario 2: The iPhone User Tempted by Cheaper Android
- **User:** iPhone ecosystem, considering Pixel for cost savings
- **Performance Agent:** iPhone 16 Pro ($999) - best camera, performance
- **Value Agent:** Google Pixel 8 ($499) - great value, excellent camera
- **Simplicity Agent:** iPhone 15 ($699) - ecosystem consistency, resale value
- **Judge:** "Switching costs: $500 in app repurchases + AirPods incompatibility. iPhone 15 is better value."

### Scenario 3: The Casual User Buying Gaming Laptop
- **User:** "Wants to game", actually plays 2hrs/week casual games
- **Performance Agent:** Gaming laptop with RTX 4070 ($1800)
- **Value Agent:** Steam Deck ($399) + decent work laptop ($600)
- **Simplicity Agent:** MacBook Air + Xbox Game Pass cloud gaming ($1099)
- **Judge:** "You're a casual gamer. Don't carry 5lb laptop daily for 2hrs/week gaming."

---

## 8. Why This Matters

TechMagi reframes electronics buying as:
- **Use-case aligned** (what you do, not what tech reviewers do)
- **Ecosystem-aware** (switching costs are real)
- **Total cost focused** (device + accessories + subscriptions + resale)
- **Proficiency-matched** (pro features you can't use aren't valuable)

It helps buyers:
- Avoid overspending on unused features
- Consider hidden costs (ecosystem switching, accessories)
- Make choices aligned with actual behavior
- Reduce buyer's remorse

---

## 9. Future Extensions

- **Real-time price tracking** (price history, deal alerts)
- **Refurbished marketplace integration**
- **Usage tracking** (connect to device analytics to verify assumptions)
- **Post-purchase check-in** ("Are you using those pro features?")
- **Trade-in value optimization**
- **Accessory recommendations** based on device choice

---

## 10. Key Differentiators

Unlike generic tech review sites:
- **Multi-perspective analysis** (specs vs value vs UX)
- **Persona-aware** (your proficiency and usage patterns)
- **Ecosystem-conscious** (switching costs quantified)
- **Reality-check focused** (you don't need what YouTubers say you need)
- **Total cost aware** (includes hidden expenses)

---

## 11. Alignment with AgentField Hackathon Criteria

✅ **New problem space:** Not a chatbot - automated backend decision engine  
✅ **Replaced complexity:** Eliminates analysis paralysis from spec overload  
✅ **High leverage:** $500-3000 decision with 3-5 year impact  
✅ **Previously impossible:** No tool considers your actual usage + ecosystem + proficiency together  

---

## 12. Name Variations

- TechMagi
- GadgetMagi
- DeviceMagi
- SpecMagi
