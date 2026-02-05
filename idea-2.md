# PRD: TechHR-Magi – AI-Powered Post-Interview Hiring Advisory System

## 1. Problem Statement

Tech hiring decisions are high-stakes and expensive to get wrong, yet they often rely on:
- **Gut feelings** after interview rounds
- **Inconsistent evaluation** across different interviewers
- **Recency bias** (last interview weighs more than earlier rounds)
- **Single-dimension focus** (hired for technical skills, fired for culture fit)

Hiring managers struggle to synthesize:
- Technical assessment results
- Behavioral interview signals
- Culture fit observations
- Red flags vs coachable gaps

As a result, companies either:
- Pass on great candidates who interviewed poorly on one dimension
- Hire strong technical performers who don't fit the team
- Make slow decisions while "waiting for consensus"

---

## 2. Proposed Solution

**TechHR-Magi** is a post-interview analysis system that provides persona-aware hiring recommendations.

After a candidate completes all interview rounds, three specialized agents analyze the results through different lenses:
- **Skills Agent** (Performance-focused): Technical capability, problem-solving
- **Team Agent** (Culture-focused): Communication, collaboration, team dynamics
- **Growth Agent** (Potential-focused): Learning ability, adaptability, trajectory

A **Judge Agent** synthesizes their recommendations based on:
- Team composition and gaps
- Role requirements and seniority level
- Company stage and values
- Diversity and hiring goals

---

## 3. System Overview

### 3.1 Core Agents

#### 🎯 Skills Agent (Technical Excellence)
- **Focus:** Technical depth, problem-solving ability, code quality
- **Analyzes:**
  - Coding challenge performance
  - System design reasoning
  - Technical depth in specialty areas
- **Output:** "Hire if you need senior expertise now"
- **Bias:** May overlook soft skills and growth potential

#### 🤝 Team Agent (Cultural Fit)
- **Focus:** Communication, collaboration, team dynamics
- **Analyzes:**
  - Behavioral interview responses
  - Communication clarity
  - Conflict resolution approach
  - Values alignment
- **Output:** "Hire if team harmony is priority"
- **Bias:** May undervalue technical gaps that can be trained

#### 🌱 Growth Agent (Future Potential)
- **Focus:** Learning velocity, adaptability, trajectory
- **Analyzes:**
  - How they approached unknown problems
  - Questions they asked
  - Self-awareness about gaps
  - Career progression pattern
- **Output:** "Hire if you can invest in development"
- **Bias:** May overestimate potential vs current capability

---

### 3.2 Agent Analysis Process

Each agent:
1. **Ingests interview data:**
   - Structured scores (1-5 ratings)
   - Interviewer notes and observations
   - Code submissions or work samples
   - Behavioral question responses

2. **Performs analysis:**
   - Identifies strengths and concerns
   - Compares against role requirements
   - Flags inconsistencies across rounds

3. **Generates recommendation:**
   - Hire / No Hire / Borderline
   - Key evidence supporting decision
   - Potential risks and mitigation strategies

---

### 3.3 Judge Agent (Context-Aware Arbiter)

The Judge Agent:
- **Reviews all three agent recommendations**
- **Considers organizational context:**
  - Team composition (need senior vs junior?)
  - Current team dynamics (need collaborator vs independent contributor?)
  - Project urgency (need impact now vs later?)
  - Hiring market conditions
  - Diversity and inclusion goals

- **Produces final recommendation:**
  - Clear hire/no-hire decision with confidence level
  - Reasoning that addresses disagreements between agents
  - Onboarding recommendations if hire
  - Suggested areas for reference checks

---

## 4. Input Data Model (PoC Scope)

### Interview Round Data Structure

```json
{
  "candidate_id": "C001",
  "role": "Senior Backend Engineer",
  "interview_rounds": [
    {
      "type": "coding_challenge",
      "score": 4,
      "notes": "Strong algorithmic thinking, clean code, good edge case handling",
      "concerns": "Took longer than expected on optimization"
    },
    {
      "type": "system_design",
      "score": 5,
      "notes": "Excellent scalability reasoning, considered trade-offs",
      "concerns": "Limited experience with microservices"
    },
    {
      "type": "behavioral",
      "score": 3,
      "notes": "Smart but somewhat arrogant, interrupted interviewer twice",
      "concerns": "May struggle with junior mentoring"
    },
    {
      "type": "cultural_fit",
      "score": 4,
      "notes": "Values align, excited about mission",
      "concerns": "Prefers working independently"
    }
  ],
  "team_context": {
    "team_size": 8,
    "seniority_mix": "2 senior, 4 mid, 2 junior",
    "current_gaps": "Need senior technical leadership",
    "team_dynamics": "Collaborative, ego-free culture"
  }
}
```

---

## 5. Hackathon PoC Implementation

### 5.1 Scope Constraints
- **Single role type** (e.g., Backend Engineer)
- **Synthetic interview data** (3-5 candidate profiles)
- **4 standard interview rounds** (Coding, System Design, Behavioral, Culture)
- **Pre-defined team context**

---

### 5.2 Technical Architecture

```
Interview Data (JSON)
        ↓
+--------------------------------+
| Skills | Team | Growth Agents |
+--------------------------------+
        ↓
  Individual Analysis
  + Self-Critique
        ↓
    Judge Agent
    (Context-Aware)
        ↓
  Final Recommendation
  + Reasoning + Risks
```

---

### 5.3 Technology Stack (Suggested)
- **Python** (AgentField framework)
- **JSON** for interview data structure
- **LLM for:**
  - Agent reasoning and analysis
  - Pattern recognition in interview notes
  - Judge decision synthesis
  - Explanation generation

---

## 6. Success Criteria (Hackathon)

- **Clear differentiation** between agent perspectives on same candidate
- **Visible trade-offs** (e.g., Skills loves them, Team has concerns)
- **Judge explains reasoning** transparently
- **Handles disagreement** (agents split 2-1)
- **Judges can test** with different team contexts

---

## 7. Demo Scenarios

### Scenario 1: The Technical Rockstar with Culture Risk
- Skills Agent: **Strong Hire** (5/5 technical)
- Team Agent: **No Hire** (arrogance, poor collaboration signals)
- Growth Agent: **Hire** (fast learner, but may plateau)
- Judge Decision: **Depends on team maturity and need**

### Scenario 2: The Solid Mid-Level with High Potential
- Skills Agent: **Borderline** (competent but not exceptional)
- Team Agent: **Strong Hire** (great communicator, humble)
- Growth Agent: **Strong Hire** (asks great questions, growth mindset)
- Judge Decision: **Hire if can invest in development**

### Scenario 3: The Safe But Unremarkable Candidate
- All agents: **Hire** (no red flags, meets bar)
- Judge: **Analyzes opportunity cost** (is "good enough" actually good?)

---

## 8. Why This Matters

TechHR-Magi reframes hiring as:
- **Multi-dimensional decision** (not just "smart enough?")
- **Context-dependent** (right for this team, at this time)
- **Evidence-based** (not gut feeling)
- **Trade-off aware** (perfect candidate doesn't exist)

It helps companies:
- Make faster decisions with more confidence
- Reduce hiring mistakes
- Surface unconscious biases in evaluation
- Build more balanced teams

---

## 9. Future Extensions

- **Real-time interview note capture** (integration with ATS)
- **Historical hire outcome tracking** (did we make the right call?)
- **Interviewer bias detection** (pattern analysis across interviews)
- **Salary recommendation** based on market + candidate strength
- **Onboarding plan generation** for new hires

---

## 10. Key Differentiators

Unlike generic hiring tools that just score candidates:
- **Multi-perspective analysis** (skills vs culture vs potential)
- **Team context-aware** (right for YOUR team, not just "good")
- **Transparent reasoning** (why we recommend X)
- **Disagreement handling** (agents debate, judge decides)

---

## 11. Alignment with AgentField Hackathon Criteria

✅ **New problem space:** Hiring is not a chatbot use case - it's backend decision-making  
✅ **Replaced complexity:** Eliminates back-and-forth consensus meetings  
✅ **High leverage:** Hiring mistakes cost 6-12 months of salary + opportunity cost  
✅ **Previously impossible:** No tool considers multi-dimensional trade-offs with team context  

---

## 12. Name Variations

- TechHR-Magi
- HireMagi
- TalentMagi
- TeamBuildMagi
