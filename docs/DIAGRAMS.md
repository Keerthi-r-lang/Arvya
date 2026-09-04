# Arvya Diagram Pack

> **Arvya — Where AI Buyers Meet AI Merchants.**
>
> These diagrams describe the governed commerce loop: agents propose and explain, merchants approve commercial actions, buyers confirm checkout, and Razorpay provides the verified payment outcome.

## 1. High-Level Architecture

```mermaid
flowchart LR
    Buyer["Buyer / Customer"] --> Web["Arvya React Workspace"]
    Merchant["Merchant"] --> Web

    subgraph Arvya["Arvya Governed Commerce Platform"]
        Web --> API["FastAPI API Layer"]
        API --> BuyerAgent["Buyer Agent"]
        API --> MerchantAgent["Merchant Growth Agent"]
        API --> DecisionCenter["AI Decision Center"]
        API --> Governance["Governance Layer"]
        Governance --> Store[("PostgreSQL")]
        BuyerAgent --> Store
        MerchantAgent --> Store
        DecisionCenter --> Store
    end

    API --> Razorpay["Razorpay Payment Links\nTest Mode"]
    Razorpay --> Webhook["Signed Razorpay Webhook"]
    Webhook --> API

    classDef actor fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef core fill:#F5F3FF,stroke:#6D4AFF,color:#0F172A
    classDef trust fill:#ECFDF5,stroke:#10B981,color:#064E3B
    classDef payment fill:#FFF7ED,stroke:#F97316,color:#7C2D12
    class Buyer,Merchant actor
    class API,BuyerAgent,MerchantAgent,DecisionCenter core
    class Governance,Store trust
    class Razorpay,Webhook payment
```

## 2. Buyer Agent Workflow

```mermaid
flowchart TD
    A["Buyer enters intent and budget"] --> B["Intent parser extracts product and category signals"]
    B --> C["Search approved merchant offers only"]
    C --> D["Compare intent relevance, confidence, coupon eligibility, and final price"]
    D --> E["Explain selected offer and alternatives"]
    E --> F{"Buyer confirms checkout?"}
    F -- "No" --> G["Keep recommendation only"]
    F -- "Yes" --> H["Revalidate approval, coupon, and payable amount server-side"]
    H --> I["Create idempotent Razorpay Test Mode Payment Link"]
    I --> J["Open hosted Razorpay checkout"]

    classDef buyer fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef check fill:#ECFDF5,stroke:#10B981,color:#064E3B
    classDef payment fill:#FFF7ED,stroke:#F97316,color:#7C2D12
    class A,B,C,D,E,G buyer
    class F,H check
    class I,J payment
```

## 3. Merchant Agent Workflow

```mermaid
flowchart TD
    A["Merchant catalog and commercial context"] --> B["Catalog Analysis Agent"]
    B --> C["Bundle Discovery Agent"]
    B --> D["Upsell Agent"]
    B --> E["Campaign Agent"]
    C --> F["Impact Estimation Agent"]
    D --> F
    E --> F
    F --> G["Recommendation with evidence, assumptions, and projected lift"]
    G --> H["Decision Center computes confidence and risk"]
    H --> I{"Merchant decision"}
    I -- "Reject" --> J["Record rejection in audit trail"]
    I -- "Approve or edit" --> K["Expose governed offer to Buyer Agent"]

    classDef agent fill:#F5F3FF,stroke:#6D4AFF,color:#0F172A
    classDef decision fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef trust fill:#ECFDF5,stroke:#10B981,color:#064E3B
    class B,C,D,E,F agent
    class G,H decision
    class I,J,K trust
```

## 4. Commerce Simulation Flow

```mermaid
flowchart LR
    A["1. Customer intent"] --> B["2. Buyer Agent"]
    B --> C["3. Catalog analysis"]
    C --> D["4. Offer discovery"]
    D --> E["5. Merchant evaluation"]
    E --> F["6. Bundle opportunity"]
    F --> G["7. Coupon validation"]
    G --> H["8. Risk check"]
    H --> I["9. Approval gate"]
    I --> J["10. Simulated payment-link step"]
    J --> K["11. Simulated payment-completion step"]
    K --> L["12. Simulated revenue outcome"]
    L --> M["13. Audit ledger update"]

    classDef live fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef govern fill:#ECFDF5,stroke:#10B981,color:#064E3B
    classDef simulated fill:#FFF7ED,stroke:#F97316,color:#7C2D12
    class A,B,C,D,E,F,G live
    class H,I,M govern
    class J,K,L simulated
```

> Simulation mode is deliberately non-financial: it never creates a real Razorpay link, captures money, or changes live revenue metrics.

## 5. Payment Link Flow

```mermaid
sequenceDiagram
    autonumber
    participant B as Buyer
    participant UI as Arvya UI
    participant API as Arvya API
    participant DB as Arvya Database
    participant R as Razorpay Test Mode

    B->>UI: Confirm checkout for approved offer
    UI->>API: POST checkout request with idempotency key
    API->>DB: Verify recommendation is merchant-approved
    API->>DB: Recompute coupon and final payable amount
    API->>DB: Check existing checkout attempt
    alt Existing safe attempt
        DB-->>API: Existing payment-link record
        API-->>UI: Return existing payment-link URL
    else New checkout attempt
        API->>R: Create Razorpay Payment Link
        R-->>API: Payment link ID and short URL
        API->>DB: Store provider response and audit event
        API-->>UI: Return hosted Razorpay link
    end
    UI-->>B: Open Razorpay Test Mode checkout
```

## 6. Governance Flow

```mermaid
flowchart TD
    A["Agent proposal"] --> B["Evidence collection"]
    B --> C["Margin protection"]
    C --> D["Inventory protection"]
    D --> E["Coupon validation"]
    E --> F["Risk scoring"]
    F --> G{"Blocking risk?"}
    G -- "Yes" --> H["Mark review or block execution"]
    G -- "No" --> I["Merchant approval gate"]
    I --> J{"Approved?"}
    J -- "No" --> K["Audit rejection; do not execute"]
    J -- "Yes" --> L["Buyer-visible governed offer"]
    L --> M["Buyer confirmation before checkout"]
    M --> N["Razorpay Payment Link request"]

    classDef guard fill:#ECFDF5,stroke:#10B981,color:#064E3B
    classDef decision fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef block fill:#FEF2F2,stroke:#EF4444,color:#7F1D1D
    class B,C,D,E,F,I,L,M guard
    class A,G,J,N decision
    class H,K block
```

## 7. Approval Workflow

```mermaid
stateDiagram-v2
    [*] --> Draft: Agent creates recommendation
    Draft --> PendingApproval: Evidence and policy checks recorded
    PendingApproval --> Rejected: Merchant rejects recommendation
    PendingApproval --> Approved: Merchant approves proposed offer
    PendingApproval --> Approved: Merchant approves edited lower price
    Rejected --> [*]: Audit retained; no commercial execution
    Approved --> BuyerVisible: Buyer Agent can discover offer
    BuyerVisible --> CheckoutRequested: Buyer confirms checkout
    CheckoutRequested --> PaymentLinkCreated: Razorpay link created safely
    PaymentLinkCreated --> Paid: Verified signed webhook
    PaymentLinkCreated --> Failed: Provider failure, cancellation, or expiry
    Failed --> CheckoutRequested: Safe retry when eligible
    Paid --> [*]: Revenue and audit updated
```

## 8. Audit Trail Flow

```mermaid
flowchart LR
    Agent["Agent action"] --> Log["Audit event builder"]
    Merchant["Merchant approval or rejection"] --> Log
    Buyer["Buyer checkout request"] --> Log
    Payment["Razorpay payment-link response"] --> Log
    Webhook["Verified Razorpay webhook"] --> Log
    Simulation["Safe commerce simulation"] --> Log
    Log --> Store[("Audit Logs")]
    Store --> Timeline["Merchant Audit Trail UI"]
    Store --> Decision["Decision Center audit references"]
    Store --> Ops["Payment operations investigation"]

    classDef source fill:#EFF6FF,stroke:#0B84D8,color:#0F172A
    classDef ledger fill:#ECFDF5,stroke:#10B981,color:#064E3B
    classDef view fill:#F5F3FF,stroke:#6D4AFF,color:#0F172A
    class Agent,Merchant,Buyer,Payment,Webhook,Simulation source
    class Log,Store ledger
    class Timeline,Decision,Ops view
```

## 9. Database ER Diagram

```mermaid
erDiagram
    MERCHANT ||--o{ PRODUCT : owns
    MERCHANT ||--o{ COUPON : configures
    MERCHANT ||--o{ AGENT_RUN : starts
    AGENT_RUN ||--o{ AGENT_ACTION : records
    AGENT_RUN ||--o{ RECOMMENDATION : produces
    RECOMMENDATION ||--o{ RECOMMENDATION_ITEM : contains
    PRODUCT ||--o{ RECOMMENDATION_ITEM : contributes_to
    MERCHANT ||--o{ PAYMENT_LINK : receives
    RECOMMENDATION ||--o{ PAYMENT_LINK : executes
    PAYMENT_LINK ||--o{ WEBHOOK_EVENT : reconciles
    MERCHANT ||--o{ AUDIT_LOG : records

    MERCHANT {
        int id PK
        string name
        string email
        string industry
        string currency
    }
    PRODUCT {
        int id PK
        int merchant_id FK
        string sku
        string name
        int price_paise
        int cost_paise
        int inventory_count
        string status
    }
    COUPON {
        int id PK
        int merchant_id FK
        string code
        int discount_percent
        int min_order_paise
        string status
    }
    AGENT_RUN {
        int id PK
        int merchant_id FK
        string status
        string model_provider
        datetime started_at
    }
    AGENT_ACTION {
        int id PK
        int agent_run_id FK
        int recommendation_id FK
        string agent_name
        string action_type
        string status
    }
    RECOMMENDATION {
        int id PK
        int merchant_id FK
        int agent_run_id FK
        string type
        string status
        float confidence_score
        datetime approved_at
    }
    RECOMMENDATION_ITEM {
        int id PK
        int recommendation_id FK
        int product_id FK
        string role
        int original_price_paise
    }
    PAYMENT_LINK {
        int id PK
        int merchant_id FK
        int recommendation_id FK
        string razorpay_payment_link_id
        int amount_paise
        string status
    }
    WEBHOOK_EVENT {
        int id PK
        string provider_event_id
        string event_type
        string payment_link_external_id
        boolean signature_verified
    }
    AUDIT_LOG {
        int id PK
        int merchant_id FK
        string actor_type
        string actor_id
        string event_type
        string entity_type
        datetime created_at
    }
```

## 10. Complete End-to-End Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant M as Merchant
    participant UI as Arvya UI
    participant G as Merchant Growth Agent
    participant D as Decision Center / Risk Engine
    participant DB as Arvya Database
    participant B as Buyer
    participant BA as Buyer Agent
    participant R as Razorpay Test Mode
    participant W as Webhook Handler
    participant A as Audit Ledger

    M->>UI: Upload or review catalogue
    UI->>DB: Persist products, costs, and inventory
    M->>UI: Run growth analysis
    UI->>G: Start specialist-agent workflow
    G->>DB: Read catalog context
    G->>DB: Write action trace and recommendations
    G->>D: Submit recommendation evidence
    D->>DB: Evaluate confidence, risk, and guardrails
    D-->>UI: Show explainable recommendation

    M->>UI: Approve, edit, or reject offer
    alt Merchant rejects
        UI->>DB: Persist rejected status
        DB->>A: Record rejection audit event
    else Merchant approves
        UI->>DB: Persist approved status
        DB->>A: Record approval audit event
        B->>UI: Enter shopping intent and budget
        UI->>BA: Search approved offers
        BA->>DB: Read approved offers and coupon rules
        BA-->>UI: Return ranked, explained offers
        B->>UI: Confirm chosen offer
        UI->>DB: Validate approval, price, coupon, and idempotency
        UI->>R: Create Payment Link
        R-->>UI: Hosted Test Mode link
        UI-->>B: Redirect to Razorpay checkout
        R->>W: Send signed payment-link webhook
        W->>W: Verify HMAC and event uniqueness
        W->>DB: Update verified payment status
        W->>A: Record Razorpay payment outcome
        A-->>M: Show ledger and audit update
    end
```

---

## Suggested use in the Buildathon demo

1. Start with the **High-Level Architecture** diagram.
2. Use the **Merchant Agent Workflow** to establish commercial value.
3. Use the **Buyer Agent Workflow** to establish customer value.
4. Show the **Governance Flow** before discussing payments.
5. Finish with the **End-to-End Sequence Diagram** and then demonstrate the live UI.
