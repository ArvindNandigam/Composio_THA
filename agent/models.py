from typing import List, Optional
from pydantic import BaseModel, Field

class AppInput(BaseModel):
    id: int
    name: str
    category: str
    hint: str

class AppResearchResult(BaseModel):
    id: int
    name: str
    category: str
    hint: str
    description: str = Field(description="One-line summary of what the app does")
    auth_methods: List[str] = Field(description="List of auth methods, e.g. ['OAuth2'], ['API Key'], ['Basic Auth'], ['None (CLI)']")
    auth_notes: str = Field(description="Brief details on auth flow, scopes, or token mechanics")
    self_serve: str = Field(description="'Self-serve', 'Partially Gated', 'Enterprise/Sales Gated', or 'Open Source / Local'")
    self_serve_detail: str = Field(description="How a developer gets credentials (free signup, credit card, sales call, developer org)")
    api_surface: str = Field(description="API type, e.g. 'REST', 'GraphQL', 'REST & GraphQL', 'CLI / Local Executable', 'Private / None'")
    api_breadth: str = Field(description="Scope of API: 'Broad (>50 endpoints)', 'Medium (10-50 endpoints)', 'Narrow (<10 endpoints)', 'CLI / Local Tool'")
    existing_mcp: bool = Field(description="Whether an official or recognized community MCP server exists")
    mcp_details: Optional[str] = Field(default="None known", description="Name/link or details of existing MCP server or 'None known'")
    mcp_url: Optional[str] = Field(default=None, description="Direct URL to official MCP repository or documentation")
    buildability: str = Field(description="'Easy (Ready today)', 'Medium (App approval / OAuth required)', 'Hard (Enterprise / Sales gated)', 'Blocked (No public API)'")
    blocker_analysis: str = Field(description="Primary blocker or technical hurdle for building a Composio toolkit")
    evidence_urls: List[str] = Field(description="List of verified docs URLs or developer portal links")
    confidence_score: float = Field(default=0.9, description="Confidence score from 0.0 to 1.0")
    verification_status: str = Field(default="Unverified", description="'Verified', 'Flagged for Human Review', or 'Corrected in Pass 2'")
    verification_notes: Optional[str] = Field(default=None, description="Notes on accuracy verification or discrepancies caught")
    human_report_status: Optional[str] = Field(default=None, description="'Verified' or 'Corrected in Audit'")
    human_report: Optional[str] = Field(default=None, description="Human verification notes or audit summary")

class VerificationAudit(BaseModel):
    app_id: int
    app_name: str
    pass1_finding: str
    pass2_finding: str
    discrepancy_found: bool
    discrepancy_type: Optional[str] = None # e.g. "Auth Misclassification", "Gating Nuance", "CLI vs REST"
    resolution: str
    verified_evidence_url: str

class VerificationAuditRecord(BaseModel):
    app_id: int
    app_name: str
    category: str
    pass1_summary: str
    discrepancy_found: bool
    discrepancy_type: str
    resolution: str
    verified_evidence_url: str
    mcp_verified_url: Optional[str] = None

