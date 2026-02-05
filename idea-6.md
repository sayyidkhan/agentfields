# PRD: SupplyMagi – B2B Vendor Selection & Procurement Advisory System

## 1. Problem Statement

B2B procurement decisions are complex, high-stakes, and often go wrong:
- **Single-dimension optimization** (cheapest vendor wins, quality suffers)
- **Hidden risks** (over-reliance on single supplier, geopolitical exposure)
- **Short-term thinking** (lowest quote today, highest cost over 3 years)
- **Relationship undervalued** (vendor responsiveness matters when things break)

Procurement teams optimize for:
- Lowest unit price
- Fastest delivery
- Meeting minimum quality standards

They ignore:
- Supply chain resilience (single point of failure)
- Total cost of quality issues (defect rates, returns, rework)
- Relationship value (response time, flexibility, problem-solving)
- Long-term pricing stability (low price now, 20% increase next year)

Result: Supplier relationships that optimize for cost but collapse under pressure.

---

## 2. Proposed Solution

**SupplyMagi** is a B2B vendor selection system that balances cost, quality, and relationship.

Three specialized agents analyze suppliers through different lenses:
- **Cost Agent** (Price Optimizer): Lowest price, bulk discounts, negotiation leverage
- **Quality Agent** (Reliability Focus): Certifications, defect rates, consistency, compliance
- **Relationship Agent** (Partnership Focus): Responsiveness, flexibility, long-term value

A **Judge Agent** selects the best fit based on:
- Company risk tolerance
- Volume and criticality of purchase
- Supply chain resilience needs
- Stage of business (startup vs enterprise)

---

## 3. System Overview

### 3.1 Core Agents

#### 💰 Cost Agent (Price Optimizer)
- **Focus:** Lowest total procurement cost, negotiation leverage
- **Optimizes for:** Unit price, bulk discounts, payment terms
- **Analyzes:**
  - Price per unit across vendors
  - Volume discount tiers
  - Payment terms (net-30 vs net-60)
  - Switching cost (lock-in contracts)
- **Bias:** Undervalues quality risk and relationship flexibility

#### ✅ Quality Agent (Reliability & Compliance)
- **Focus:** Consistent quality, certifications, low defect rates
- **Optimizes for:** Zero-defect delivery, compliance, certifications
- **Analyzes:**
  - Quality certifications (ISO 9001, industry-specific)
  - Historical defect rates and recall history
  - Audit reports and compliance records
  - Consistency of delivery quality
- **Bias:** May recommend premium vendors when mid-tier is sufficient

#### 🤝 Relationship Agent (Partnership & Flexibility)
- **Focus:** Long-term partnership, responsiveness, problem-solving
- **Optimizes for:** Vendor reliability when things go wrong
- **Analyzes:**
  - Response time to inquiries and issues
  - Flexibility on custom orders or rush deliveries
  - Track record of problem resolution
  - Willingness to co-innovate or adapt
- **Bias:** May prioritize soft factors over measurable cost/quality

---

### 3.2 Agent Analysis Process

Each agent:
1. **Ingests procurement context:**
   - Product/material specifications
   - Volume requirements
   - Quality standards needed
   - Budget constraints
   - Criticality to business

2. **Analyzes vendor options:**
   - Scores vendors based on their priority lens
   - Projects 12-36 month total cost of ownership
   - Identifies risks specific to each vendor

3. **Generates recommendation:**
   - Top 1-2 vendor choices with reasoning
   - Trade-offs and risk factors
   - Contract terms to negotiate
   - Self-critique of own bias

---

### 3.3 Judge Agent (Risk-Aware Arbiter)

The Judge Agent:
- **Reviews all three recommendations**
- **Applies context filters:**
  - **Criticality:** Is this component mission-critical or commodity?
  - **Volume risk:** What happens if vendor can't deliver?
  - **Quality impact:** What's the cost of a defective batch?
  - **Relationship need:** Do we need flexibility or just reliability?
  - **Diversification:** Are we over-dependent on one supplier?

- **Selects final recommendation:**
  - Balances cost, quality, and relationship
  - Considers supply chain resilience
  - May recommend multi-vendor strategy
  - Explains trade-offs transparently

---

## 4. Input Data Model (PoC Scope)

### Procurement Request
```json
{
  "purchase": {
    "item": "Custom injection-molded plastic components",
    "annual_volume": 100000,
    "unit_budget_max": 2.50,
    "quality_standard": "ISO 9001 required",
    "lead_time_max_days": 45
  },
  "business_context": {
    "company_stage": "Series A",
    "criticality": "high",
    "product_dependency": "blocking for production",
    "current_suppliers": 1,
    "risk_tolerance": "medium"
  },
  "priorities": ["quality", "reliability", "cost"]
}
```

### Vendor Database (Simplified for PoC)
```json
{
  "vendors": [
    {
      "name": "BudgetMold Co.",
      "price_per_unit": 1.80,
      "certifications": ["None"],
      "defect_rate": 2.5,
      "response_time_hours": 48,
      "location": "Overseas",
      "lead_time_days": 60
    },
    {
      "name": "QualityPlastics Inc.",
      "price_per_unit": 2.40,
      "certifications": ["ISO 9001", "ISO 14001"],
      "defect_rate": 0.3,
      "response_time_hours": 4,
      "location": "Domestic",
      "lead_time_days": 30
    },
    {
      "name": "PartnerMold Ltd.",
      "price_per_unit": 2.10,
      "certifications": ["ISO 9001"],
      "defect_rate": 0.8,
      "response_time_hours": 12,
      "location": "Regional",
      "lead_time_days": 40,
      "flexibility": "high"
    }
  ]
}
```

---

## 5. Hackathon PoC Implementation

### 5.1 Scope Constraints
- **Single procurement category** (e.g., manufacturing components)
- **3-5 vendor options** (pre-defined dataset)
- **Simplified TCO model** (12-month horizon)
- **Static vendor data** (no real-time pricing)

---

### 5.2 Technical Architecture

```
Procurement Request + Business Context
        ↓
   Vendor Database
        ↓
+----------------------------------+
| Cost | Quality | Relationship   |
+----------------------------------+
        ↓
  Vendor Analysis + Risk Mapping
        ↓
   Judge Agent
   (Risk-Aware)
        ↓
  Final Recommendation
  + TCO + Risk Assessment
```

---

### 5.3 Technology Stack (Suggested)
- **Python** (AgentField framework)
- **JSON** for vendor data and procurement context
- **Pandas** for TCO calculations
- **LLM for:**
  - Agent reasoning and trade-off analysis
  - Risk assessment synthesis
  - Judge decision explanation
  - Contract term recommendations

---

## 6. Success Criteria (Hackathon)

- **Clear agent disagreement** (Cost picks cheapest, Quality picks premium)
- **TCO comparison** (not just unit price)
- **Risk quantification** (defect cost, supply disruption impact)
- **Judge explains trade-offs** with business context
- **Handles different criticality levels** (commodity vs mission-critical)

---

## 7. Demo Scenarios

### Scenario 1: The Penny-Wise, Pound-Foolish Supplier
- **Context:** High-volume, mission-critical component
- **Cost Agent:** BudgetMold ($1.80/unit, saves $60k/year!)
- **Quality Agent:** QualityPlastics ($2.40/unit, 0.3% defect rate)
- **Relationship Agent:** PartnerMold ($2.10/unit, flexible, responsive)
- **Judge:** "2.5% defect rate = $15k in returns + production delays. QualityPlastics saves money."

### Scenario 2: The Commodity Purchase (Cost Should Win)
- **Context:** Low-criticality, non-blocking purchase
- **Cost Agent:** Cheapest vendor ($0.50/unit)
- **Quality Agent:** Premium vendor ($0.80/unit)
- **Relationship Agent:** Mid-tier vendor ($0.65/unit)
- **Judge:** "This is a commodity. Cost Agent is right. Quality premium not justified here."

### Scenario 3: The Single Supplier Risk
- **Context:** Company relies on one supplier for 80% of components
- **Cost Agent:** Stay with current (cheapest)
- **Quality Agent:** Switch to certified supplier
- **Relationship Agent:** Dual-source strategy
- **Judge:** "Supply chain risk is high. Recommend dual-sourcing even at 10% cost premium."

---

## 8. Why This Matters

SupplyMagi reframes procurement as:
- **Multi-dimensional optimization** (cost + quality + relationship)
- **Risk-aware** (supply chain resilience, not just unit economics)
- **TCO-focused** (defect costs, relationship value, long-term pricing)
- **Context-dependent** (commodity vs critical components need different strategies)

It helps companies:
- Avoid catastrophic supplier failures
- Balance cost optimization with risk management
- Build resilient supply chains
- Make evidence-based vendor decisions

---

## 9. Future Extensions

- **Real-time vendor performance tracking** (defect rates, delivery times)
- **Supplier financial health monitoring** (bankruptcy risk detection)
- **Geopolitical risk assessment** (tariffs, shipping disruptions)
- **Contract negotiation guidance** (based on multi-agent analysis)
- **Post-purchase review** (did vendor perform as expected?)
- **Multi-vendor optimization** (when to diversify vs consolidate)

---

## 10. Key Differentiators

Unlike generic procurement platforms:
- **Multi-perspective analysis** (cost vs quality vs relationship)
- **Risk-aware** (considers supply chain resilience)
- **TCO-focused** (defect costs, not just unit price)
- **Context-dependent** (criticality drives recommendation)
- **Transparent trade-offs** (explains why not cheapest)

---

## 11. Alignment with AgentField Hackathon Criteria

✅ **New problem space:** Not a chatbot - autonomous procurement decision engine  
✅ **Replaced complexity:** Eliminates RFP evaluation paralysis  
✅ **High leverage:** Procurement is 40-60% of company costs  
✅ **Previously impossible:** No tool balances cost/quality/relationship with risk context  

---

## 12. Why This Could Be a Standalone Business

B2B procurement is a **massive market**:
- $13 trillion annual B2B procurement in US alone
- Companies waste 5-10% on poor supplier decisions
- High willingness to pay for risk reduction

**Revenue model:**
- Per-procurement license (one-time or subscription)
- Enterprise annual contracts
- Integration with ERP systems (SAP, Oracle)
- Supplier network effects (vendor ratings improve with scale)

**Competitive moats:**
- Supplier performance data (grows more valuable over time)
- Industry-specific vendor knowledge
- Integration into procurement workflows

---

## 13. Name Variations

- SupplyMagi
- VendorMagi
- ProcureMagi
- SourceMagi
