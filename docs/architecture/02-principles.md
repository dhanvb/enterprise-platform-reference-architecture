P01  Capability before product

## P01 - Capability Before Product

Architecture decisions should begin with the capability required
by the organization rather than the product used to implement it.

For example, the architectural requirement may be:

> Desired application state must be stored in version control and
> continuously reconciled with the runtime environment.

Argo CD and Flux are possible implementations of this capability.

The architecture should not make application teams dependent on
implementation-specific behavior unless there is a justified
reason.

This reduces the cost of replacing components during the
platform lifecycle.

P02  Platform as a product
P03  Standardize the paved road
P04  Clear platform/application ownership
P05  Build once, promote the same artifact
P06  Declarative desired state
P07  Security by default
P08  Least privilege
P09  Observability by default
P10  Failure and recovery are design requirements
P11  Everything important should be auditable
P12  Operability is part of architecture
P13  Automate repeatable operations
P14  Minimize implementation coupling
P15  Design for component replacement