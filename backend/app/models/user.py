"""
SevaSetu AI — Database Models (SQLAlchemy ORM)
Author: Rahul Jha | Made in India 🇮🇳

Tables:
  users            - Registered citizens and admins
  query_history    - Every AI interaction stored here
  query_feedback   - User ratings on AI responses
  schemes          - Government scheme master data
  user_schemes     - User↔scheme eligibility mapping
  documents        - Uploaded documents metadata
  document_fields  - OCR-extracted field values
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    Float, DateTime, Enum, ForeignKey, JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


# ── ENUMS ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    USER  = "user"
    ADMIN = "admin"

class SchemeCategory(str, enum.Enum):
    AGRICULTURE = "agriculture"
    HEALTH      = "health"
    EDUCATION   = "education"
    HOUSING     = "housing"
    WOMEN       = "women"
    FINANCE     = "finance"
    EMPLOYMENT  = "employment"
    SOCIAL      = "social"
    DIGITAL     = "digital"

class DocumentStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class EligibilityStatus(str, enum.Enum):
    ELIGIBLE     = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    PARTIAL      = "partial"
    UNKNOWN      = "unknown"


# ── USER MODEL ────────────────────────────────────────────────────────────────

class User(Base):
    """
    Registered user (citizen or admin).
    Stores profile, auth, and preference info.
    """
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    mobile        = Column(String(15),  unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    state         = Column(String(60), nullable=True)
    language      = Column(String(5), default="en")          # en | hi | mr
    avatar_url    = Column(String(500), nullable=True)
    is_active     = Column(Boolean, default=True)
    is_verified   = Column(Boolean, default=False)           # email verified
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    queries       = relationship("QueryHistory",  back_populates="user", cascade="all, delete-orphan")
    documents     = relationship("Document",      back_populates="user", cascade="all, delete-orphan")
    user_schemes  = relationship("UserScheme",    back_populates="user", cascade="all, delete-orphan")
    feedbacks     = relationship("QueryFeedback", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"


# ── QUERY HISTORY MODEL ───────────────────────────────────────────────────────

class QueryHistory(Base):
    """
    Stores every question asked by a user along with the AI response.
    Used for history display, analytics, and RAG context building.
    """
    __tablename__ = "query_history"

    id          = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question    = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    category    = Column(String(50), nullable=True, index=True)    # voter_id, pan, scheme, etc.
    language    = Column(String(5), default="en")
    confidence  = Column(Float, default=0.0)                       # RAG confidence score 0-1
    sources     = Column(Text, nullable=True)                      # Comma-separated source titles
    is_bookmarked = Column(Boolean, default=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user     = relationship("User",          back_populates="queries")
    feedback = relationship("QueryFeedback", back_populates="query",  uselist=False)

    def __repr__(self):
        return f"<QueryHistory id={self.id} user={self.user_id} category={self.category}>"


# ── QUERY FEEDBACK MODEL ──────────────────────────────────────────────────────

class QueryFeedback(Base):
    """User ratings and comments on AI responses — used for model improvement."""
    __tablename__ = "query_feedback"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    query_id   = Column(Integer, ForeignKey("query_history.id", ondelete="CASCADE"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id",          ondelete="CASCADE"), nullable=False)
    rating     = Column(Integer, nullable=False)        # 1-5 stars
    is_helpful = Column(Boolean, default=True)
    comment    = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    query = relationship("QueryHistory", back_populates="feedback")
    user  = relationship("User",         back_populates="feedbacks")


# ── SCHEME MODEL ──────────────────────────────────────────────────────────────

class Scheme(Base):
    """
    Master table of all central and state government schemes.
    Admin-managed. Used for eligibility matching and RAG knowledge base.
    """
    __tablename__ = "schemes"

    id                   = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name                 = Column(String(200), nullable=False, index=True)
    short_name           = Column(String(50),  nullable=True)
    description          = Column(Text, nullable=False)
    category             = Column(Enum(SchemeCategory), nullable=False, index=True)
    ministry             = Column(String(200), nullable=True)
    benefits             = Column(Text, nullable=True)               # What citizen gets
    eligibility_criteria = Column(JSON, nullable=True)               # Structured eligibility rules
    eligibility_text     = Column(Text, nullable=True)               # Human-readable criteria
    required_documents   = Column(JSON, nullable=True)               # List of required docs
    application_url      = Column(String(500), nullable=True)
    helpline             = Column(String(50), nullable=True)
    application_steps    = Column(Text, nullable=True)               # Step-by-step guide
    states_applicable    = Column(JSON, nullable=True)               # null = all India
    max_income           = Column(Float, nullable=True)              # For income-based schemes
    min_age              = Column(Integer, nullable=True)
    max_age              = Column(Integer, nullable=True)
    gender               = Column(String(10), nullable=True)         # male | female | all
    is_active            = Column(Boolean, default=True, index=True)
    is_central           = Column(Boolean, default=True)             # Central vs State scheme
    launch_date          = Column(DateTime(timezone=True), nullable=True)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())
    updated_at           = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_schemes = relationship("UserScheme", back_populates="scheme")

    def __repr__(self):
        return f"<Scheme id={self.id} name={self.name} category={self.category}>"


# ── USER-SCHEME ELIGIBILITY MODEL ─────────────────────────────────────────────

class UserScheme(Base):
    """
    Maps users to schemes they've checked eligibility for.
    Stores the calculated eligibility score and status.
    """
    __tablename__ = "user_schemes"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.id",    ondelete="CASCADE"), nullable=False)
    scheme_id         = Column(Integer, ForeignKey("schemes.id",  ondelete="CASCADE"), nullable=False)
    eligibility_score = Column(Float, default=0.0)               # 0.0 - 1.0
    status            = Column(Enum(EligibilityStatus), default=EligibilityStatus.UNKNOWN)
    checked_at        = Column(DateTime(timezone=True), server_default=func.now())
    notes             = Column(Text, nullable=True)               # AI explanation of eligibility

    # Relationships
    user   = relationship("User",   back_populates="user_schemes")
    scheme = relationship("Scheme", back_populates="user_schemes")

    def __repr__(self):
        return f"<UserScheme user={self.user_id} scheme={self.scheme_id} status={self.status}>"


# ── DOCUMENT MODEL ────────────────────────────────────────────────────────────

class Document(Base):
    """
    Uploaded documents by users. Stores file metadata and OCR results.
    Actual files stored on disk/S3, only paths saved here.
    """
    __tablename__ = "documents"

    id             = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_name  = Column(String(255), nullable=False)
    stored_name    = Column(String(255), nullable=False, unique=True)  # UUID-based filename
    file_path      = Column(String(500), nullable=False)
    file_type      = Column(String(10), nullable=False)              # pdf | jpg | png
    file_size_kb   = Column(Integer, nullable=True)
    service_type   = Column(String(50), nullable=True)               # voter_id | pan | passport
    doc_type       = Column(String(50), nullable=True)               # aadhaar | pan | voter_id
    ocr_status     = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING)
    extracted_text = Column(Text, nullable=True)                     # Raw OCR text
    extracted_fields = Column(JSON, nullable=True)                   # Structured extracted fields
    verification_score = Column(Float, nullable=True)                # 0-1 completeness score
    is_valid       = Column(Boolean, nullable=True)
    missing_fields = Column(JSON, nullable=True)                     # List of missing fields
    uploaded_at    = Column(DateTime(timezone=True), server_default=func.now())
    processed_at   = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user   = relationship("User",            back_populates="documents")
    fields = relationship("DocumentField",   back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document id={self.id} user={self.user_id} type={self.doc_type} status={self.ocr_status}>"


# ── DOCUMENT FIELD MODEL ──────────────────────────────────────────────────────

class DocumentField(Base):
    """
    Individual field-value pairs extracted from a document via OCR.
    Enables granular verification checks.
    """
    __tablename__ = "document_fields"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name  = Column(String(100), nullable=False)    # name | dob | aadhaar_number | address
    field_value = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    confidence  = Column(Float, nullable=True)            # OCR confidence for this field

    # Relationships
    document = relationship("Document", back_populates="fields")

    def __repr__(self):
        return f"<DocumentField doc={self.document_id} field={self.field_name}>"


# ── PASSWORD RESET TOKEN MODEL ───────────────────────────────────────────────

class PasswordResetToken(Base):
    """Short-lived, single-use password reset token stored as a SHA-256 hash."""
    __tablename__ = "password_reset_tokens"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at    = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
