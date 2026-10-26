
# Enterprise Platform Technology Evaluation Framework

**Document ID:** ARC-006  
**Status:** Reference Architecture  
**Decision:** ADR-002

## 1. Objective

Establish an evidence-based process for selecting enterprise platform technologies against business requirements, architectural capabilities and operating constraints.

## 2. Fundamental Principle

Architectural capabilities must be defined before technology selection.

A product's features do not automatically constitute business requirements.

## 3. Evaluation Boundaries

Evaluate candidates within appropriate capability categories.

### Runtime Platforms

Examples:

- Kubernetes distributions
- OpenShift
- Managed Kubernetes services
- Alternative managed application runtimes

### Build and Continuous Integration

Examples:

- GitHub Actions
- GitLab CI/CD
- Azure Pipelines
- Jenkins

### Desired-State Reconciliation

Examples:

- Argo CD
- Flux
- Other declarative deployment controllers

A CI engine is not a direct substitute for a GitOps reconciliation controller.

An enterprise delivery architecture may require both.

## 4. Evaluation Stages

### Stage 1: Establish Context

Document business requirements, workloads, security obligations, hosting constraints, organizational expertise, budget and support expectations.

### Stage 2: Determine Capability Coverage

Map requirements to capabilities using the capability catalog and traceability matrix.

### Stage 3: Apply Mandatory Gates

Each candidate receives:

- PASS
- FAIL
- UNKNOWN

FAIL prevents selection unless an authorized exception is accepted.

UNKNOWN prevents final approval until resolved.

### Stage 4: Evaluate Eligible Candidates

Candidates are scored from 1 to 5 against agreed criteria.

| Score | Interpretation |
|---|---|
| 1 | Major requirement gaps |
| 2 | Partial capability fit |
| 3 | Meets baseline requirements |
| 4 | Meets requirements with meaningful advantages |
| 5 | Strong demonstrated fit |

Only verified or explicitly evidenced findings should receive scores in a real procurement exercise.

### Stage 5: Calculate Weighted Score

Weighted result:

SUM(criterion weight × candidate score) / SUM(criteria weights)

The reference weights are:

| Criterion | Weight |
|---|---:|
| Security and governance | 25 |
| Operational maintainability | 20 |
| Functional capability | 20 |
| Reliability and lifecycle | 15 |
| Total cost of ownership | 10 |
| Organizational skills | 10 |
| **Total** | **100** |

These weights are reference assumptions.

### Stage 6: Sensitivity Analysis

Test whether the decision changes when:

- Security importance increases.
- Staffing limitations dominate.
- Licensing cost becomes more important.
- Lifecycle and support requirements change.

A ranking that reverses under small weight adjustments indicates decision sensitivity.

### Stage 7: Record Decision

Document:

- Selected candidate or approach
- Rejected alternatives
- Supporting evidence
- Mandatory gates
- Cost and operational implications
- Risks and assumptions
- Decision authority
- Reevaluation triggers

## 5. Worked Example: Runtime Strategy

This is a hypothetical decision exercise, not a product benchmark.

### Scenario

A fictional enterprise operates:

- 20 teams
- 100 services
- Three environments
- Mixed stateful and stateless workloads
- A small central platform operations team

The enterprise has not yet selected its runtime.

### Candidate Strategies

A: Modular Kubernetes-based platform

B: Integrated OpenShift-based platform

For this exercise, both are assumed to have met the mandatory eligibility gates.

This assumption is not evidence that either product passes the gates for a real organization.

### Illustrative Scores

| Criterion | Weight | Strategy A | Strategy B |
|---|---:|---:|---:|
| Security and governance | 25 | 3 | 4 |
| Operational maintainability | 20 | 3 | 4 |
| Functional capability | 20 | 4 | 4 |
| Reliability and lifecycle | 15 | 3 | 4 |
| Total cost | 10 | 5 | 2 |
| Organizational skills | 10 | 4 | 3 |

Weighted results:

Strategy A = 3.50 / 5

Strategy B = 3.70 / 5

The initial result favors Strategy B under these assumed scores.

However, a different cost model or organizational capability profile may change the outcome.

### Sensitivity Exercise

Change only the criterion weights:

- Security: 15
- Maintainability: 15
- Functionality: 15
- Reliability: 10
- Cost: 35
- Skills: 10

Under these hypothetical weights:

Strategy A = 3.95 / 5

Strategy B = 3.70 / 5

The ranking reverses.

### Interpretation

The example demonstrates why product rankings depend on organizational priorities and supported evidence.

It does not demonstrate that OpenShift is more secure or more reliable than any particular Kubernetes distribution.

The scores are assumptions created to test the evaluation framework.

Actual candidate scores must come from product evidence, validated cost estimates, proof-of-concept results and organizational review.

## 6. TCO Considerations

Technology costs include:

- Infrastructure
- Licensing and subscriptions
- Implementation engineering
- Integration
- Operations staffing
- Training
- Support
- Security maintenance
- Backup and recovery
- Upgrades and replacement

Free software does not necessarily mean low total cost.

Commercial software does not automatically provide superior operational value.

## 7. Reference Evaluation Status

The technology scorecard is an unassessed candidate inventory.

The worked example demonstrates the mathematics and sensitivity of an architectural decision.

Neither is a completed vendor assessment.

## 8. Decision

Select technologies through verified requirements and explicit capability evaluation.

Do not select a runtime, CI system or GitOps product solely because it is popular or familiar.

See ADR-002.
