"""
Trust Plane — Policy, authorization, secrets, audit, and approval management.

Built on: OPA (policy), OpenFGA (fine-grained authz), Vault (secrets),
          Keycloak (identity/SSO).

Responsibilities:
- Policy decision-making separated from application logic
- Relationship-based access control (RBAC + ReBAC)
- Centralized secrets with rotation and dynamic generation
- Evidence packs for every business-critical decision
- Approval classes / Reversibility classes / Sensitivity classes
- Tool verification ledger
- PDPL/NCA-aware control mapping
"""
