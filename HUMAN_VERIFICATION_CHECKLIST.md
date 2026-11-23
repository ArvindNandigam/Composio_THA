# Human Spot-Check Verification Sheet (Composio Take-Home)

Use this quick manual audit sheet to cross-check the agent's findings against real documentation. Each app below represents a distinct architectural or commercial gating pattern.

---

### 1. Twenty (#5) - CRM and Sales
- **Agent Finding:** Open Source / Local | REST & GraphQL | API Key, OAuth2 | Verdict: Easy (Ready today)
- **Direct Docs URL:** https://docs.twenty.com
- **What to verify:** Open the docs, check Settings > Developers. You will see workspace API keys and self-hosting GraphQL endpoints.
- [ ] Verified by hand

---

### 2. Salesforce (#1) - CRM and Sales
- **Agent Finding:** Partially Gated | REST & SOAP | OAuth2 (Connected Apps) | Verdict: Medium
- **Direct Docs URL:** https://developer.salesforce.com/docs
- **What to verify:** Free Developer Edition orgs exist, but production requires Connected App OAuth2 configuration with specific scopes.
- [ ] Verified by hand

---

### 3. Plain (#17) - Support and Helpdesk
- **Agent Finding:** Self-serve | GraphQL | Workspace Machine Tokens / API Key | Verdict: Easy
- **Direct Docs URL:** https://www.plain.com/docs/api-reference
- **What to verify:** Check API reference. Notice it is an engineering-first GraphQL API with instant workspace machine tokens. (Note: Our verification loop caught that Pass 1 search initially confused this with a word puzzle game).
- [ ] Verified by hand

---

### 4. Amazon Selling Partner API (#49) - Ecommerce
- **Agent Finding:** Partially Gated | REST (SP-API) | LWA (Login with Amazon) + AWS IAM SigV4 | Verdict: Medium/Hard
- **Direct Docs URL:** https://developer-docs.amazon.com/sp-api
- **What to verify:** Check developer registration requirements. You will see that obtaining SP-API credentials requires an active Amazon Professional Selling Account ($39.99/mo) and an AWS IAM role ARN.
- [ ] Verified by hand

---

### 5. Sherlock (#58) - Data, SEO and Scraping
- **Agent Finding:** Open Source / Local | CLI / Local Executable | No Auth (CLI/None) | Verdict: Easy (Local MCP)
- **Direct Docs URL:** https://github.com/sherlock-project/sherlock
- **What to verify:** It is a pure Python OSINT CLI tool on GitHub with `sherlock <username>`. No API key or HTTP server needed.
- [ ] Verified by hand

---

### 6. Stripe (#81) - Finance and Fintech
- **Agent Finding:** Self-serve | REST | API Keys (Publishable/Secret) + OAuth2 Connect | Verdict: Easy
- **Direct Docs URL:** https://stripe.com/docs/api
- **What to verify:** Instant signup yields immediate `sk_test_...` sandbox keys with zero gating.
- [ ] Verified by hand

---

### 7. DealCloud (#10) - CRM and Sales
- **Agent Finding:** Enterprise / Sales Gated | REST | Enterprise OAuth2 / API Key | Verdict: Hard
- **Direct Docs URL:** https://api.docs.dealcloud.com
- **What to verify:** DealCloud is part of Intapp; API access requires an enterprise subscription, institutional client approval, and partner contract.
- [ ] Verified by hand

---

### 8. Google Ads (#31) - Marketing and Ads
- **Agent Finding:** Partially Gated | gRPC & REST | OAuth2 + Developer Token | Verdict: Medium
- **Direct Docs URL:** https://developers.google.com/google-ads/api/docs/first-call/overview
- **What to verify:** Notice that an OAuth2 access token alone cannot make API calls-it must be accompanied by a Manager Account Developer Token.
- [ ] Verified by hand

---

### 9. NotebookLM (#91) - AI, Research and Media
- **Agent Finding:** Closed / Enterprise Gated | Private / Enterprise API | Verdict: Blocked (No Public API)
- **Direct Docs URL:** https://notebooklm.google.com
- **What to verify:** Consumer NotebookLM has no public standalone REST API for custom tool calling; enterprise usage runs through Gemini Enterprise / Vertex AI.
- [ ] Verified by hand

---

### 10. Mermaid CLI (#98) - AI, Research and Media
- **Agent Finding:** Open Source / Local | Node.js CLI (`mmdc`) | No Auth (CLI/None) | Verdict: Easy (Local MCP)
- **Direct Docs URL:** https://github.com/mermaid-js/mermaid-cli
- **What to verify:** It is an npm package (`@mermaid-js/mermaid-cli`) that generates diagrams from terminal commands. Zero API auth needed.
- [ ] Verified by hand
