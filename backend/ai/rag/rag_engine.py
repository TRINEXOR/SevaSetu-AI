"""
SevaSetu AI — RAG (Retrieval Augmented Generation) Engine
Author: Rahul Jha | Made in India 🇮🇳

This module implements the complete RAG pipeline:
1. Query preprocessing and language detection
2. Embedding generation using sentence-transformers
3. Semantic search in ChromaDB vector store
4. Context augmentation and prompt engineering
5. Response generation via Gemini / OpenAI API
6. Response post-processing and translation
"""

import asyncio
import logging
import hashlib
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from langdetect import detect

from app.core.config import settings

logger = logging.getLogger(__name__)


class SevasetuRAGEngine:
    """
    Complete RAG pipeline for SevaSetu AI.
    Combines ChromaDB vector search with Gemini LLM for accurate,
    grounded answers about government services.
    """

    # Government services knowledge base - embedded at startup
    KNOWLEDGE_BASE = [
        # ── VOTER ID ──────────────────────────────────────────────────────────
        {
            "id": "voter-new-registration",
            "title": "Voter ID New Registration",
            "content": """
                New Voter ID registration process in India:
                1. Visit voters.eci.gov.in or Voter Helpline app
                2. Click on "New Registration for voters of 18+ age" (Form 6)
                3. Fill personal details: Name, DOB, address, mobile
                4. Upload documents: Aadhaar card, passport photo, address proof
                5. Submit and note your reference number
                6. BLO (Booth Level Officer) will verify within 30 days
                7. Download eEPIC card from portal or receive physical card

                Documents required: Aadhaar Card, Recent passport photo,
                Address proof (utility bill/bank statement), Age proof (DOB certificate)
                Eligibility: Indian citizen, 18+ years, not already registered
                Fee: Free of cost
                Processing time: 30-60 days
            """,
            "category": "voter_id",
            "tags": ["voter id", "EPIC card", "electoral roll", "form 6"],
        },
        {
            "id": "voter-correction",
            "title": "Voter ID Correction",
            "content": """
                Voter ID card correction process (Form 8):
                1. Visit voters.eci.gov.in
                2. Go to "Correction of entries in existing electoral roll"
                3. Fill Form 8 with correct information
                4. Upload supporting documents for the correction
                5. Submit and track status

                Types of corrections and required documents:
                - Name correction: Aadhaar card, PAN card, school certificate
                - Address change: Utility bill, bank statement, Aadhaar
                - Date of birth correction: Birth certificate, school marksheet
                - Photo update: New passport size photo

                Offline option: Visit nearest ERO/BLO office with Form 8
                Fee: Free
                Processing time: 30-45 days
            """,
            "category": "voter_id",
            "tags": ["voter id correction", "form 8", "electoral roll correction"],
        },
        # ── PAN CARD ──────────────────────────────────────────────────────────
        {
            "id": "pan-new",
            "title": "PAN Card New Application",
            "content": """
                PAN Card new application process for individuals:
                Online application:
                1. Visit tin.tin.nsdl.com or utiitsl.com
                2. Select "Apply for New PAN (Form 49A)" for Indian citizens
                3. Fill personal details: Full name, DOB, address, father's name
                4. Upload documents and photo
                5. Pay fee: ₹107 (Indian address) or ₹1017 (foreign address)
                6. PAN delivered in 15-20 working days

                Documents required:
                - Identity proof: Aadhaar card (preferred), Passport, Voter ID
                - Address proof: Aadhaar, utility bill (3 months), bank statement
                - Date of birth proof: Birth certificate, 10th marksheet
                - 2 passport size photos
                - Signature scan

                Eligibility: All Indian citizens, companies, entities
                Purpose: Income tax filing, bank account, financial transactions
                Note: Link PAN with Aadhaar at incometax.gov.in
            """,
            "category": "pan_card",
            "tags": ["PAN card", "form 49A", "income tax", "permanent account number"],
        },
        # ── PASSPORT ──────────────────────────────────────────────────────────
        {
            "id": "passport-fresh",
            "title": "Fresh Passport Application",
            "content": """
                Fresh Passport application process in India:
                Step 1: Register on passportindia.gov.in
                Step 2: Fill online application form (Form-1)
                Step 3: Pay fee online: ₹1,500 (36 pages) or ₹2,000 (60 pages)
                Step 4: Book appointment at nearest PSK (Passport Seva Kendra) or POPSK
                Step 5: Visit PSK with original documents on appointment day
                Step 6: Police verification conducted
                Step 7: Passport dispatched within 30-45 days

                Documents required at PSK:
                - Aadhaar Card (mandatory)
                - Birth Certificate or School Leaving Certificate (DOB proof)
                - 10th/12th Certificate (for educational qualification column)
                - Address proof (Aadhaar/ Utility bill)
                - Existing passport (if any)
                - 2 recent passport photos (white background)

                Tatkal Passport:
                - Extra fee: ₹3,500 (36 pages) or ₹4,000 (60 pages)
                - Processing in 1-3 working days after police verification
                - Need to show urgency proof (flight ticket, medical, etc.)
                - Available at all PSK locations
            """,
            "category": "passport",
            "tags": ["passport", "PSK", "Tatkal", "passportindia.gov.in", "travel document"],
        },
        # ── BIRTH CERTIFICATE ─────────────────────────────────────────────────
        {
            "id": "birth-certificate",
            "title": "Birth Certificate Application",
            "content": """
                Birth Certificate registration and application in India:

                For births within 21 days (Free registration):
                - Register at local Municipal Corporation / Gram Panchayat
                - Hospital usually provides form; parents fill and submit
                - Certificate issued free of charge

                For delayed registration (after 21 days):
                District/Municipal Corporation level:
                1. Visit Registrar of Births and Deaths office
                2. Submit application with supporting documents
                3. Affidavit required for delay
                4. Pay applicable fee (₹50-200 varies by state)

                Online application (Maharashtra):
                - Visit aaplesarkar.mahaonline.gov.in
                - Revenue → Certificates → Birth Certificate
                - Upload required documents
                - Processing: 7-15 working days

                Documents for delayed registration:
                - Hospital discharge summary / Nursing home certificate
                - Aadhaar card of parents
                - Ration card
                - School leaving certificate (if child is older)
                - Affidavit on stamp paper
                - Witness declarations

                Certificate uses: School admission, passport, marriage, inheritance
            """,
            "category": "birth_certificate",
            "tags": ["birth certificate", "registration", "civil registration"],
        },
        # ── AYUSHMAN BHARAT ───────────────────────────────────────────────────
        {
            "id": "ayushman-bharat-pmjay",
            "title": "Ayushman Bharat PMJAY - Health Insurance",
            "content": """
                Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY):

                Benefits:
                - Health insurance coverage: ₹5 lakh per family per year
                - Cashless treatment at 25,000+ empanelled hospitals
                - Covers 1,949 medical procedures
                - Pre-existing diseases covered from Day 1
                - No cap on family size or age
                - Secondary and tertiary care hospitalization

                Eligibility (based on SECC-2011 data):
                - Rural: Households with certain deprivation criteria
                - Urban: 11 occupational categories (rag pickers, domestic workers, etc.)
                - Automatically included if in SECC database

                How to check eligibility:
                1. Visit pmjay.gov.in → "Am I Eligible"
                2. Enter mobile number and Aadhaar
                3. Or call toll-free: 14555

                How to get Ayushman Card:
                1. Verify eligibility at pmjay.gov.in
                2. Visit nearest Common Service Centre (CSC)
                3. Provide Aadhaar, SECC data, family details
                4. Biometric verification
                5. Ayushman card issued instantly or within 15 days

                Hospitals: Find at pmjay.gov.in → Find Hospital
            """,
            "category": "health_scheme",
            "tags": ["Ayushman Bharat", "PMJAY", "health insurance", "AB-PMJAY", "Modicare"],
        },
        # ── PM KISAN ─────────────────────────────────────────────────────────
        {
            "id": "pm-kisan-yojana",
            "title": "PM Kisan Samman Nidhi Yojana",
            "content": """
                PM Kisan Samman Nidhi Yojana - Income support for farmers:

                Benefits:
                - ₹6,000 per year in 3 equal installments of ₹2,000
                - Directly credited to bank account every 4 months
                - No intermediary — Direct Benefit Transfer

                Eligibility:
                ✅ Small and marginal farmers with cultivable land
                ✅ Indian citizens
                ✅ Landholding up to 2 hectares
                ❌ Taxpayers (income tax payers) NOT eligible
                ❌ Pensioners receiving ₹10,000+/month NOT eligible
                ❌ Institutional landholders NOT eligible
                ❌ Current/former government employees NOT eligible

                How to apply:
                1. Visit pmkisan.gov.in
                2. Click "New Farmer Registration"
                3. Enter Aadhaar number and state
                4. Fill land and bank details
                5. Submit and verify via OTP
                OR visit Common Service Centre (CSC) or State Agriculture office

                Required documents:
                - Aadhaar card
                - Land records (7/12 extract, khata number)
                - Bank account passbook
                - Mobile number

                Check status: pmkisan.gov.in → Beneficiary Status
                Helpline: 155261 / 1800115526 (Toll Free)
            """,
            "category": "agriculture_scheme",
            "tags": ["PM Kisan", "farmer scheme", "agriculture", "direct benefit transfer"],
        },
        # ── INCOME CERTIFICATE ────────────────────────────────────────────────
        {
            "id": "income-certificate",
            "title": "Income Certificate Application",
            "content": """
                Income Certificate — State government document for income proof:

                Purpose: Required for government job applications, scheme eligibility,
                fee concessions, bank loans, EWS certificate, etc.

                How to apply (Maharashtra):
                Online: aaplesarkar.mahaonline.gov.in
                Offline: Tehsildar office / SDM office

                Documents required:
                - Aadhaar card (identity proof)
                - Ration card (family details)
                - Salary slips (last 3 months) / Bank statement
                - Self-declaration affidavit on stamp paper
                - Application form (available at office or online)

                Fee: ₹20-50 (varies by state)
                Processing time: 7-15 working days
                Valid for: 1 year (must be renewed annually)

                Categories of Income:
                - Salaried: Submit salary certificate from employer
                - Self-employed: ITR or business income proof
                - Daily wage: Self-declaration with witness

                States with online portals:
                - Maharashtra: aaplesarkar.mahaonline.gov.in
                - UP: edistrict.up.gov.in
                - Delhi: edistrict.delhigovt.nic.in
                - Karnataka: nadakacheri.karnataka.gov.in
            """,
            "category": "certificate",
            "tags": ["income certificate", "EWS", "tehsildar", "revenue certificate"],
        },
        # ── CASTE CERTIFICATE ─────────────────────────────────────────────────
        {
            "id": "caste-certificate",
            "title": "Caste Certificate (SC/ST/OBC)",
            "content": """
                Caste Certificate for SC, ST, OBC categories:

                Purpose: Required for educational reservations, government jobs,
                scheme benefits, fee concessions.

                Application process:
                Online: State e-district portals
                Offline: Tehsildar / SDM / District Collector office

                Documents required:
                - Aadhaar card
                - Ration card (showing caste)
                - Birth certificate
                - Father's caste certificate (if available)
                - School leaving certificate
                - Self-declaration
                - Residential proof (last 15 years in some states)

                Fee: ₹10-50 varies by state
                Processing: 15-30 working days
                Validity: Permanent (lifetime validity for SC/ST)

                Important: Caste must be in state government schedule/list
                Different states may have different OBC lists
                Central OBC list and State OBC list are separate

                Appeals: SDM → District Collector → High Court
            """,
            "category": "certificate",
            "tags": ["caste certificate", "SC ST OBC", "reservation", "backward class"],
        },
        # ── DOMICILE CERTIFICATE ──────────────────────────────────────────────
        {
            "id": "domicile-certificate",
            "title": "Domicile Certificate",
            "content": """
                Domicile Certificate — Proof of state residence:

                Purpose: Required for state government jobs (local reservations),
                educational admissions, state schemes, property purchase.

                Eligibility: Must have resided in state for minimum period
                (varies: Maharashtra 15 years, UP 5 years, etc.)

                Application:
                Online: State portals (aaplesarkar.mahaonline.gov.in for Maharashtra)
                Offline: Tehsildar / SDM office

                Documents:
                - Aadhaar card
                - Birth certificate (if born in state)
                - School certificates showing state address
                - Ration card
                - Property documents (if owned)
                - Rent agreement / utility bills (for rental)
                - Voter ID showing state address

                Fee: ₹20-100 varies by state
                Processing: 15-30 days
                Validity: Permanent (for birth domicile) or 3 years (for residence)

                Note: Married women can get domicile of husband's state
            """,
            "category": "certificate",
            "tags": ["domicile certificate", "residence certificate", "state domicile"],
        },
    ]

    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.ai_client = None
        self.ai_model = None
        self._initialized = False

    async def initialize(self):
        """Initialize ChromaDB, embedding model, and Gemini AI."""
        if self._initialized:
            return
        try:
            logger.info("🔧 Initializing SevaSetu RAG Engine...")

            # Initialize embedding model
            logger.info("📊 Loading sentence transformer model...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

            # Initialize ChromaDB
            logger.info("🗄️ Connecting to ChromaDB...")
            self.chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"description": "SevaSetu AI Government Schemes Knowledge Base"},
            )

            # Index knowledge base if empty
            if self.collection.count() == 0:
                await self._index_knowledge_base()
            else:
                logger.info(f"✅ ChromaDB has {self.collection.count()} documents")

            # Initialize Gemini
            if settings.GEMINI_API_KEY:
                self.ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.ai_model = settings.AI_MODEL
                logger.info(f"✅ Gemini AI initialized ({settings.AI_MODEL})")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not set — using rule-based responses")

            self._initialized = True
            logger.info("✅ SevaSetu RAG Engine fully initialized")

        except Exception as e:
            logger.error(f"❌ RAG Engine initialization failed: {e}")
            raise

    async def _index_knowledge_base(self):
        """Index all knowledge base documents into ChromaDB."""
        logger.info(f"📥 Indexing {len(self.KNOWLEDGE_BASE)} knowledge base documents...")

        for doc in self.KNOWLEDGE_BASE:
            embedding = self.embedding_model.encode(
                doc["title"] + " " + doc["content"],
                normalize_embeddings=True,
            ).tolist()

            self.collection.add(
                ids=[doc["id"]],
                documents=[doc["content"]],
                embeddings=[embedding],
                metadatas=[{
                    "title": doc["title"],
                    "category": doc["category"],
                    "tags": ",".join(doc["tags"]),
                }],
            )
        logger.info(f"✅ Indexed {len(self.KNOWLEDGE_BASE)} documents into ChromaDB")

    async def query(
        self,
        user_query: str,
        user_context: Optional[dict] = None,
        language: str = "en",
        top_k: int = 3,
    ) -> dict:
        """
        Main RAG query pipeline:
        1. Detect language & preprocess query
        2. Generate query embedding
        3. Semantic search in ChromaDB
        4. Build augmented prompt
        5. Generate response via Gemini
        6. Post-process and return
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Step 1: Detect language if not provided
            try:
                detected_lang = detect(user_query)
                if detected_lang in ["hi", "mr"]:
                    language = detected_lang
            except Exception:
                pass

            # Step 2: Translate query to English for embedding (if Hindi/Marathi)
            query_for_embedding = user_query
            # Note: In production, use Google Translate API here

            # Step 3: Generate embedding
            query_embedding = self.embedding_model.encode(
                query_for_embedding,
                normalize_embeddings=True,
            ).tolist()

            # Step 4: Semantic search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            # Extract retrieved documents
            retrieved_docs = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    retrieved_docs.append({
                        "content": doc,
                        "title": results["metadatas"][0][i].get("title", ""),
                        "relevance": 1 - results["distances"][0][i],  # Convert distance to similarity
                    })

            # Filter by relevance threshold
            relevant_docs = [d for d in retrieved_docs if d["relevance"] > 0.3]

            # Step 5: Build context for LLM
            context = "\n\n---\n\n".join([
                f"SOURCE: {d['title']}\n{d['content']}"
                for d in relevant_docs
            ])

            # Step 6: Generate response
            response_text = await self._generate_response(
                query=user_query,
                context=context,
                user_context=user_context,
                language=language,
            )

            # Step 7: Compute confidence score
            confidence = max([d["relevance"] for d in relevant_docs], default=0.5)

            return {
                "answer": response_text,
                "sources": [d["title"] for d in relevant_docs],
                "confidence": round(confidence, 3),
                "language": language,
                "retrieved_docs_count": len(relevant_docs),
            }

        except Exception as e:
            logger.error(f"❌ RAG query error: {e}", exc_info=True)
            return {
                "answer": self._fallback_response(user_query),
                "sources": [],
                "confidence": 0.5,
                "language": language,
                "error": str(e),
            }

    async def _generate_response(
        self,
        query: str,
        context: str,
        user_context: Optional[dict],
        language: str,
    ) -> str:
        """Generate response using Gemini with RAG context."""

        # Language instruction
        lang_map = {
            "en": "English",
            "hi": "Hindi (use Devanagari script)",
            "mr": "Marathi (use Devanagari script)",
        }
        lang_instruction = lang_map.get(language, "English")

        # Build the system prompt
        system_prompt = f"""You are SevaSetu AI, an expert assistant helping Indian citizens with government services and schemes.
You are developed by Rahul Jha and Made in India 🇮🇳.

IMPORTANT INSTRUCTIONS:
1. Answer ONLY based on the provided context. Do not hallucinate.
2. Respond in {lang_instruction}
3. Use simple, easy-to-understand language
4. Format responses with numbered steps, bullet points where helpful
5. Always include required documents list when relevant
6. Mention official website URLs when available
7. Be helpful, empathetic, and respectful — address users as "Aap" in Hindi/Marathi
8. If you don't know, say "I don't have information about this. Please visit your nearest government office."
9. Always end with helpful contact info (helpline numbers, websites)
10. Keep responses concise but complete — maximum 400 words

CONTEXT FROM GOVERNMENT KNOWLEDGE BASE:
{context if context else "No specific information found in the knowledge base."}

USER PROFILE:
State: {user_context.get('state', 'Not specified') if user_context else 'Not specified'}
Previous queries: {user_context.get('recent_queries', '') if user_context else ''}
"""

        prompt = f"{system_prompt}\n\nCITIZEN QUERY: {query}\n\nASSISTANT RESPONSE:"

        # Use Gemini if available
        if self.ai_model:
            try:
                response = await self.ai_client.aio.models.generate_content(
                    model=self.ai_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=settings.AI_MAX_TOKENS,
                    ),
                )
                return (response.text or "").strip()
            except Exception as e:
                logger.error(f"⚠️ Gemini error: {e} — using fallback")

        # Fallback: rule-based response from retrieved context
        if context:
            return f"Based on government guidelines:\n\n{context[:1000]}...\n\n📞 For more help, call 1076 (National Helpline) or visit your nearest CSC."

        return self._fallback_response(query)

    def _fallback_response(self, query: str) -> str:
        """Rule-based fallback when AI is unavailable."""
        query_lower = query.lower()

        if "voter" in query_lower:
            return "🗳️ For Voter ID help, visit voters.eci.gov.in or call 1950. You can register, correct, or download your EPIC card online."
        elif "pan" in query_lower:
            return "💳 For PAN Card, visit tin.tin.nsdl.com or utiitsl.com. Apply online with Aadhaar, DOB proof, and photos. Fee: ₹107."
        elif "passport" in query_lower:
            return "📘 For Passport, visit passportindia.gov.in. Book appointment, pay fee, and visit nearest PSK. Tatkal available in 1-3 days."
        elif "kisan" in query_lower or "farmer" in query_lower:
            return "🌾 PM Kisan: Visit pmkisan.gov.in for registration. Get ₹6,000/year in 3 installments. Helpline: 155261."
        elif "ayushman" in query_lower or "health" in query_lower:
            return "🏥 Ayushman Bharat: Check eligibility at pmjay.gov.in or call 14555. Get ₹5 lakh free health coverage."
        else:
            return "🙏 I'm here to help with government services! Ask about Voter ID, PAN Card, Passport, Ayushman Bharat, PM Kisan, Birth Certificate, Income Certificate, or any government scheme."

    async def add_document_to_knowledge_base(
        self,
        doc_id: str,
        title: str,
        content: str,
        category: str,
        tags: list,
    ) -> bool:
        """Admin function: Add new scheme/service to knowledge base."""
        if not self._initialized:
            await self.initialize()
        try:
            embedding = self.embedding_model.encode(
                title + " " + content,
                normalize_embeddings=True,
            ).tolist()
            self.collection.upsert(
                ids=[doc_id],
                documents=[content],
                embeddings=[embedding],
                metadatas=[{"title": title, "category": category, "tags": ",".join(tags)}],
            )
            logger.info(f"✅ Added document to RAG: {title}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            return False


# Singleton instance
rag_engine = SevasetuRAGEngine()
