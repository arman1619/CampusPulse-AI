# Implementation Gantt Plan

```mermaid
gantt
    title CampusPulse AI SWE7303 delivery plan
    dateFormat  YYYY-MM-DD
    section Foundation
    Requirements and architecture      :done, a1, 2026-07-13, 7d
    Repository and service contracts   :done, a2, after a1, 7d
    section Application
    Auth / RBAC / database             :done, b1, 2026-07-27, 7d
    Feedback / workflow / notifications:done, b2, 2026-08-01, 7d
    AI triage and evaluation           :done, b3, 2026-08-04, 6d
    LLM assistant and RAG guardrails   :done, b4, 2026-08-10, 5d
    Frontend integration               :done, b5, 2026-08-04, 11d
    section DevOps
    Docker and local integration       :c1, 2026-08-12, 4d
    Jenkins and security gates         :c2, 2026-08-13, 4d
    Terraform / AWS infrastructure     :c3, 2026-08-14, 5d
    Blue-green / rollback / monitoring :c4, 2026-08-18, 4d
    section Verification
    AWS deployment evidence            :d1, 2026-08-20, 4d
    Failure / rollback demonstration   :d2, 2026-08-22, 2d
    Report, reflection, references     :d3, 2026-08-20, 8d
    Final audit and submission         :milestone, d4, 2026-08-29, 0d
```

Dates are a project planning baseline. The group should update actual progress/evidence rather than presenting the diagram as historical fact where work was completed at different times.
