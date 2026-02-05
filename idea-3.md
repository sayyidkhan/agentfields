# PRD: WheelMagi – Persona-Aware Car Purchase Advisory System

## 1. Problem Statement

Car buying is one of the most expensive and regret-prone consumer decisions, yet buyers consistently:
- **Buy for their aspirational self** (sports car for weekend drives, but they commute daily)
- **Ignore total cost of ownership** (insurance, maintenance, depreciation)
- **Overweight emotional factors** (brand prestige, aesthetics) vs practical needs
- **Underestimate usage patterns** (think they need SUV, mostly solo commute)

Most car recommendation tools optimize for:
- Best specs at price point
- Highest safety ratings
- Best reviews

They ignore:
- Your actual driving behavior vs stated preferences
- Hidden costs that matter more than sticker price
- Life stage changes (kids, aging parents, moving)
- Environmental impact vs stated values

Result: Buyers frequently regret their purchase within 6-12 months.

---

## 2. Proposed Solution

**WheelMagi** is a persona-aware car purchase advisory system that prevents buyer's remorse.

Three specialized agents analyze car options through different lenses:
- **Thrill Agent** (Experience-focused): Performance, driving dynamics, prestige
- **Practical Agent** (TCO-focused): Reliability, costs, resale value
- **Future Agent** (Long-term focused): EVs, sustainability, tech, regulatory trends

A **Judge Agent** weighs recommendations based on:
- Actual usage patterns (not just stated needs)
- Financial health (affordability stress test)
- Life stage and stability
- Value alignment (environmental claims vs actions)

---

## 3. System Overview

### 3.1 Core Agents

#### 🔥 Thrill Agent (Driving Experience)
- **Focus:** Performance, handling, brand prestige, driving pleasure
- **Optimizes for:** Fun, status, weekend drives, enthusiast features
- **Data sources:**
  - 0-60 times, horsepower, handling reviews
  - Brand perception and resale prestige
  - Driving experience reviews
- **Bias:** Overweights emotional satisfaction, underweights practicality

#### 💰 Practical Agent (Total Cost of Ownership)
- **Focus:** Reliability, maintenance costs, insurance, depreciation
- **Optimizes for:** Lowest TCO, maximum utility per dollar
- **Data sources:**
  - Reliability ratings (Consumer Reports, JD Power)
  - Insurance cost estimates
  - Fuel economy (MPG or kWh/mile)
  - Maintenance schedules and costs
  - Depreciation curves
- **Bias:** May recommend boring but sensible choices

#### 🌱 Future Agent (Long-term & Sustainability)
- **Focus:** EV transition, tech features, environmental impact, future-proofing
- **Optimizes for:** Lower emissions, tech longevity, regulatory compliance
- **Data sources:**
  - EV vs ICE comparisons
  - Carbon footprint calculations
  - Tech feature roadmaps (ADAS, self-driving)
  - Future resale value in EV transition
- **Bias:** May overestimate EV adoption speed

---

### 3.2 Agent Analysis Process

Each agent:
1. **Reviews candidate vehicles** (filtered by budget and basic needs)
2. **Scores options** based on their priority lens
3. **Projects scenarios:**
   - 5-year ownership costs
   - Lifestyle compatibility
   - Regret risk factors
4. **Self-critiques:**
   - "I'm biased toward X, but here's the downside..."
   - Trade-offs and failure modes

---

### 3.3 Judge Agent (Reality-Check Arbiter)

The Judge Agent:
- **Reviews all three recommendations**
- **Applies reality filters:**
  - **Usage analysis:** Commute distance, parking situation, passenger needs
  - **Financial stress test:** Can you afford it if income drops 20%?
  - **Life stage fit:** Planning kids? Moving cities? Aging parents?
  - **Values alignment:** You say environment matters - does your choice reflect that?

- **Selects recommendation** that:
  - Minimizes regret risk
  - Aligns with actual behavior patterns
  - Balances emotional and practical needs
  - Fits financial reality (not just budget)

---

## 4. Input Data Model (PoC Scope)

### User Profile
```json
{
  "budget": {
    "max_price": 45000,
    "preferred_payment": "finance",
    "monthly_max": 700
  },
  "usage_patterns": {
    "daily_commute_miles": 30,
    "weekly_trips": "mostly_solo",
    "parking": "street_parking",
    "annual_mileage": 12000
  },
  "life_stage": {
    "age": 32,
    "family_size": 2,
    "kids_planned": true,
    "job_stability": "stable",
    "moving_likelihood": "low"
  },
  "preferences": {
    "stated_priorities": ["fun_to_drive", "good_mpg", "reliable"],
    "brand_preference": "no_preference",
    "environmental_concern": "moderate"
  },
  "financial_health": {
    "savings_months": 6,
    "debt_to_income": 0.25,
    "risk_tolerance": "medium"
  }
}
```

### Vehicle Database (Simplified for PoC)
- 10-15 representative vehicles across categories
- Pre-populated data: price, MPG, reliability scores, insurance estimates

---

## 5. Hackathon PoC Implementation

### 5.1 Scope Constraints
- **Single buyer persona** (demo with 2-3 variations)
- **Pre-filtered vehicle set** (10-15 cars across segments)
- **Simplified TCO model** (5-year ownership)
- **No real-time pricing** (static data)

---

### 5.2 Technical Architecture

```
User Profile + Preferences
        ↓
  Vehicle Database
        ↓
+-----------------------------------+
| Thrill | Practical | Future Agents|
+-----------------------------------+
        ↓
  Analysis + TCO Projections
        ↓
   Judge Agent
   (Reality-Check)
        ↓
  Final Recommendation
  + Reasoning + Regret Risk
```

---

### 5.3 Technology Stack (Suggested)
- **Python** (AgentField framework)
- **Pandas** for TCO calculations
- **JSON** for vehicle and user data
- **LLM for:**
  - Agent reasoning and trade-off analysis
  - Judge synthesis and explanation
  - Regret risk assessment

---

## 6. Success Criteria (Hackathon)

- **Clear agent disagreement** (Thrill picks sports car, Practical picks Camry)
- **Judge explains trade-offs** transparently
- **Regret risk quantified** (e.g., "30% chance you regret this in 12 months")
- **TCO comparison** shown (not just sticker price)
- **Handles persona shifts** (change commute distance → different recommendation)

---

## 7. Demo Scenarios

### Scenario 1: The Enthusiast Who Shouldn't Buy a Sports Car
- **User:** 30yo, says wants "fun car", 50-mile daily commute
- **Thrill Agent:** Mazda MX-5 Miata (fun to drive!)
- **Practical Agent:** Honda Accord Hybrid (boring but saves $4k/year in gas)
- **Future Agent:** Tesla Model 3 (EV, tech, future-proof)
- **Judge:** "You drive 25k miles/year. Miata is expensive joy. Consider Accord or Model 3."

### Scenario 2: The Family Planner Who Doesn't Need an SUV Yet
- **User:** 28yo couple, no kids yet but "planning soon"
- **Thrill Agent:** Mazda CX-5 (stylish crossover)
- **Practical Agent:** Toyota Corolla (save money now, buy SUV when pregnant)
- **Future Agent:** RAV4 Hybrid (compromise, efficient)
- **Judge:** "You're 2-3 years from needing space. Save $300/month now."

### Scenario 3: The EV Buyer Without Home Charging
- **User:** Says "wants to go green", lives in apartment, street parking
- **Thrill Agent:** Meh (EVs not thrilling yet except Tesla)
- **Practical Agent:** Hybrid (Prius) - practicality without charging hassle
- **Future Agent:** EV (do it for the planet!)
- **Judge:** "No home charging = poor EV experience. Hybrid is greener than you think."

---

## 8. Why This Matters

WheelMagi reframes car buying as:
- **Behavior-aligned decision** (what you actually do vs what you think you want)
- **TCO-aware** (5-year cost, not just monthly payment)
- **Regret prevention** (emotional satisfaction + practical needs)
- **Values consistency check** (do your actions match stated values?)

It helps buyers:
- Avoid expensive mistakes
- See hidden trade-offs
- Make decisions they're happy with long-term
- Reduce cognitive dissonance

---

## 9. Future Extensions

- **Real-time pricing integration** (Edmunds, Kelley Blue Book APIs)
- **Insurance quote API** (personalized rates)
- **Driving pattern tracking** (integrate with phone GPS data)
- **Post-purchase check-in** ("Are you still happy? Any regrets?")
- **Marketplace integration** (direct listings based on recommendation)
- **Lease vs buy analysis**

---

## 10. Key Differentiators

Unlike generic car recommendation sites:
- **Multi-perspective analysis** (emotion vs practicality vs future)
- **Persona-aware** (your actual behavior, not generic buyer)
- **TCO-focused** (not just sticker price or monthly payment)
- **Regret prevention** (explicitly models buyer's remorse risk)
- **Values alignment** (calls out inconsistencies)

---

## 11. Alignment with AgentField Hackathon Criteria

✅ **New problem space:** Car buying isn't a chatbot - it's a high-stakes autonomous decision system  
✅ **Replaced complexity:** Eliminates endless research paralysis and buyer's remorse  
✅ **High leverage:** $30-50k decision with 5-10 year impact  
✅ **Previously impossible:** No tool stress-tests your life situation vs stated preferences  

---

## 12. Name Variations

- WheelMagi
- AutoMagi
- DriveMagi
- CarMagi
