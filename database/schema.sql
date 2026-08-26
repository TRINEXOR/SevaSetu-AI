-- ============================================================
-- SevaSetu AI — MySQL Database Schema
-- Author: Rahul Jha | Made in India 🇮🇳
-- ============================================================

CREATE DATABASE IF NOT EXISTS sevasetu_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sevasetu_db;

-- ── USERS ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id              INT           NOT NULL AUTO_INCREMENT,
    name            VARCHAR(100)  NOT NULL,
    email           VARCHAR(150)  NOT NULL,
    mobile          VARCHAR(15)   NOT NULL,
    password_hash   VARCHAR(255)  NOT NULL,
    role            ENUM('user','admin') NOT NULL DEFAULT 'user',
    state           VARCHAR(60),
    language        VARCHAR(5)    NOT NULL DEFAULT 'en',
    avatar_url      VARCHAR(500),
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at      DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      DATETIME(6)   ON UPDATE CURRENT_TIMESTAMP(6),
    last_login_at   DATETIME(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email  (email),
    UNIQUE KEY uq_users_mobile (mobile),
    INDEX idx_users_role      (role),
    INDEX idx_users_state     (state),
    INDEX idx_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── PASSWORD RESET TOKENS ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          INT          NOT NULL AUTO_INCREMENT,
    user_id     INT          NOT NULL,
    token_hash  CHAR(64)     NOT NULL,
    expires_at  DATETIME(6)  NOT NULL,
    used_at     DATETIME(6)  NULL,
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_reset_token_hash (token_hash),
    INDEX idx_reset_user (user_id),
    CONSTRAINT fk_reset_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── QUERY HISTORY ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS query_history (
    id              INT           NOT NULL AUTO_INCREMENT,
    user_id         INT           NOT NULL,
    question        TEXT          NOT NULL,
    ai_response     LONGTEXT      NOT NULL,
    category        VARCHAR(50),
    language        VARCHAR(5)    NOT NULL DEFAULT 'en',
    confidence      FLOAT         NOT NULL DEFAULT 0.0,
    sources         TEXT,
    is_bookmarked   BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at      DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX idx_qh_user_id   (user_id),
    INDEX idx_qh_category  (category),
    INDEX idx_qh_created   (created_at),
    CONSTRAINT fk_qh_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── QUERY FEEDBACK ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS query_feedback (
    id          INT         NOT NULL AUTO_INCREMENT,
    query_id    INT         NOT NULL,
    user_id     INT         NOT NULL,
    rating      TINYINT     NOT NULL,
    is_helpful  BOOLEAN     NOT NULL DEFAULT TRUE,
    comment     TEXT,
    created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_feedback_query_user (query_id, user_id),
    CONSTRAINT fk_fb_query  FOREIGN KEY (query_id) REFERENCES query_history(id) ON DELETE CASCADE,
    CONSTRAINT fk_fb_user   FOREIGN KEY (user_id)  REFERENCES users(id)         ON DELETE CASCADE,
    CONSTRAINT chk_rating   CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── SCHEMES ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS schemes (
    id                      INT          NOT NULL AUTO_INCREMENT,
    name                    VARCHAR(200) NOT NULL,
    short_name              VARCHAR(50),
    description             TEXT         NOT NULL,
    category                ENUM('agriculture','health','education','housing','women',
                                 'finance','employment','social','digital') NOT NULL,
    ministry                VARCHAR(200),
    benefits                TEXT,
    eligibility_criteria    JSON,
    eligibility_text        TEXT,
    required_documents      JSON,
    application_url         VARCHAR(500),
    helpline                VARCHAR(50),
    application_steps       TEXT,
    states_applicable       JSON         COMMENT 'NULL = all India',
    max_income              DOUBLE,
    min_age                 INT,
    max_age                 INT,
    gender                  VARCHAR(10)  DEFAULT 'all',
    is_active               BOOLEAN      NOT NULL DEFAULT TRUE,
    is_central              BOOLEAN      NOT NULL DEFAULT TRUE,
    launch_date             DATE,
    created_at              DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at              DATETIME(6)  ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    INDEX idx_schemes_category  (category),
    INDEX idx_schemes_is_active (is_active),
    FULLTEXT INDEX ft_schemes_search (name, description, benefits)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── USER SCHEMES (eligibility mapping) ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS user_schemes (
    id                  INT          NOT NULL AUTO_INCREMENT,
    user_id             INT          NOT NULL,
    scheme_id           INT          NOT NULL,
    eligibility_score   FLOAT        NOT NULL DEFAULT 0.0,
    status              ENUM('eligible','not_eligible','partial','unknown') DEFAULT 'unknown',
    checked_at          DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    notes               TEXT,
    PRIMARY KEY (id),
    UNIQUE KEY uq_user_scheme (user_id, scheme_id),
    CONSTRAINT fk_us_user   FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    CONSTRAINT fk_us_scheme FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── DOCUMENTS ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS documents (
    id                  INT          NOT NULL AUTO_INCREMENT,
    user_id             INT          NOT NULL,
    original_name       VARCHAR(255) NOT NULL,
    stored_name         VARCHAR(255) NOT NULL,
    file_path           VARCHAR(500) NOT NULL,
    file_type           VARCHAR(10)  NOT NULL,
    file_size_kb        INT,
    service_type        VARCHAR(50),
    doc_type            VARCHAR(50),
    ocr_status          ENUM('pending','processing','completed','failed') DEFAULT 'pending',
    extracted_text      LONGTEXT,
    extracted_fields    JSON,
    verification_score  FLOAT,
    is_valid            BOOLEAN,
    missing_fields      JSON,
    uploaded_at         DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    processed_at        DATETIME(6),
    PRIMARY KEY (id),
    UNIQUE KEY uq_stored_name (stored_name),
    INDEX idx_docs_user        (user_id),
    INDEX idx_docs_service     (service_type),
    INDEX idx_docs_ocr_status  (ocr_status),
    CONSTRAINT fk_docs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ── DOCUMENT FIELDS ────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS document_fields (
    id           INT          NOT NULL AUTO_INCREMENT,
    document_id  INT          NOT NULL,
    field_name   VARCHAR(100) NOT NULL,
    field_value  TEXT,
    is_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
    confidence   FLOAT,
    PRIMARY KEY (id),
    INDEX idx_df_document (document_id),
    CONSTRAINT fk_df_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- SEED DATA — Government Schemes
-- ============================================================

INSERT INTO schemes (name, short_name, description, category, ministry, benefits,
    eligibility_text, application_url, helpline, is_central, is_active, max_income, gender)
VALUES

('PM Kisan Samman Nidhi Yojana', 'PM Kisan',
 'Direct income support of Rs 6000/year to small and marginal farmers in 3 installments of Rs 2000 each.',
 'agriculture', 'Ministry of Agriculture & Farmers Welfare',
 'Rs 6,000 per year (3 x Rs 2,000) directly to bank account via DBT',
 'Small/marginal farmers with cultivable landholding upto 2 hectares. Not eligible: income taxpayers, institutional landholders, pensioners receiving Rs 10,000+/month.',
 'https://pmkisan.gov.in', '155261', TRUE, TRUE, NULL, 'all'),

('Ayushman Bharat - PM Jan Arogya Yojana', 'AB-PMJAY',
 'World''s largest health insurance scheme providing Rs 5 lakh free treatment per family at 25,000+ hospitals.',
 'health', 'Ministry of Health and Family Welfare',
 'Rs 5 lakh per family per year for hospitalization. Cashless at 25,000+ hospitals. Pre-existing diseases covered.',
 'Based on SECC-2011 data. Rural: households with specific deprivation criteria. Urban: 11 occupational categories.',
 'https://pmjay.gov.in', '14555', TRUE, TRUE, NULL, 'all'),

('PM Jan Dhan Yojana', 'PMJDY',
 'National mission for financial inclusion ensuring access to banking services to all households.',
 'finance', 'Ministry of Finance',
 'Zero balance account, RuPay debit card, Rs 2 lakh accidental insurance, Rs 30,000 life insurance, overdraft facility.',
 'All Indian citizens without a bank account. No income limit.',
 'https://pmjdy.gov.in', '1800-11-0001', TRUE, TRUE, NULL, 'all'),

('PM Awas Yojana - Urban', 'PMAY-U',
 'Affordable housing for urban poor through credit-linked subsidy and direct benefit transfer.',
 'housing', 'Ministry of Housing & Urban Affairs',
 'Interest subsidy 6.5% for EWS/LIG, 4% for MIG-I, 3% for MIG-II. Max loan: Rs 12 lakh (EWS/LIG).',
 'EWS: Annual income < Rs 3 lakh. LIG: Rs 3-6 lakh. MIG-I: Rs 6-12 lakh. MIG-II: Rs 12-18 lakh. Should not own pucca house.',
 'https://pmaymis.gov.in', '1800-11-6163', TRUE, TRUE, 1800000, 'all'),

('Beti Bachao Beti Padhao', 'BBBP',
 'National campaign to address declining child sex ratio and promote welfare and education of girl child.',
 'women', 'Ministry of Women and Child Development',
 'Awareness programs, scholarships, conditional cash transfers for education of girl child.',
 'All families with girl child. Focus on districts with low child sex ratio.',
 'https://wcd.nic.in/bbbp-schemes', '181', TRUE, TRUE, NULL, 'female'),

('Sukanya Samriddhi Yojana', 'SSY',
 'Small savings scheme for girl child with high interest rate (8.2% p.a.) and tax benefits.',
 'finance', 'Ministry of Finance',
 '8.2% interest rate, tax-free maturity, Rs 250 minimum deposit, Rs 1.5 lakh maximum/year.',
 'Parents/guardians of girl child below 10 years. Max 2 accounts per family.',
 'https://www.nsiindia.gov.in', '18004250076', TRUE, TRUE, NULL, 'female'),

('PM Mudra Yojana', 'PMMY',
 'Collateral-free loans for micro and small enterprises. Shishu (< Rs 50K), Kishor (Rs 50K-5L), Tarun (Rs 5L-10L).',
 'finance', 'Ministry of Finance',
 'Loans up to Rs 10 lakh without collateral. 3 categories: Shishu, Kishor, Tarun.',
 'Non-farm micro/small enterprise. Individuals, partnership, proprietary, small manufacturing units.',
 'https://www.mudra.org.in', '1800-180-1111', TRUE, TRUE, NULL, 'all'),

('Kisan Credit Card', 'KCC',
 'Credit facility for farmers to meet agriculture and allied activity needs at subsidised interest.',
 'agriculture', 'Ministry of Agriculture & Farmers Welfare',
 'Revolving credit up to Rs 3 lakh at 4% interest (2% subvention + 3% prompt repayment). Insurance coverage.',
 'All farmers — individual/joint borrowers who are owner cultivators. Tenant farmers, sharecroppers, SHGs.',
 'https://pmkisan.gov.in/KCC.aspx', '155261', TRUE, TRUE, NULL, 'all'),

('Pradhan Mantri Matru Vandana Yojana', 'PMMVY',
 'Maternity benefit programme providing Rs 5,000 cash incentive for first live birth.',
 'women', 'Ministry of Women and Child Development',
 'Rs 5,000 in 3 installments for first live birth. Additional Rs 6,000 under JSY for institutional delivery.',
 'Pregnant women and lactating mothers for first living child. Not eligible: central/state government employees.',
 'https://pmmvy.wcd.gov.in', '7998799804', TRUE, TRUE, NULL, 'female'),

('Atal Pension Yojana', 'APY',
 'Guaranteed minimum pension scheme for unorganised sector workers. Pension Rs 1000-5000/month from age 60.',
 'finance', 'Ministry of Finance',
 'Guaranteed minimum pension Rs 1,000-5,000/month. Same pension for spouse on death. Rs 1.7-8.5 lakh return of corpus.',
 'Indian citizens aged 18-40 years. Not a member of any statutory social security scheme. Has savings bank account.',
 'https://www.npscra.nsdl.co.in', '1800-110-069', TRUE, TRUE, NULL, 'all'),

('PM Scholarship Scheme', 'PMSS',
 'Scholarship for wards of ex-servicemen and ex-coast guard personnel for professional degree courses.',
 'education', 'Ministry of Defence',
 'Rs 3,000/month (boys) and Rs 3,500/month (girls). Duration: 1-5 years based on course.',
 'Wards and widows of ex-servicemen/ex-coast guard. Studying first professional degree (BE, MBBS, BBA, etc.). Min 60% in qualifying exam.',
 'https://ksb.gov.in', '011-26173215', TRUE, TRUE, NULL, 'all'),

('PM Garib Kalyan Yojana', 'PMGKY',
 'Free food grain distribution scheme under NFSA for eligible poor families across India.',
 'social', 'Ministry of Consumer Affairs, Food and Public Distribution',
 '5 kg free rice/wheat per person per month (in addition to NFSA entitlement). Extended for eligible beneficiaries.',
 'NFSA beneficiaries — PHH (Priority Household) and AAY (Antyodaya Anna Yojana) card holders.',
 'https://dfpd.gov.in', '1967', TRUE, TRUE, NULL, 'all');


-- ============================================================
-- SEED DATA — Admin User
-- ============================================================

-- Admin user (password: Admin@SevaSetu1 → bcrypt hash)
INSERT INTO users (name, email, mobile, password_hash, role, state, language, is_active, is_verified)
VALUES (
    'Rahul Jha',
    'admin@sevasetu.ai',
    '9999999999',
    '$2b$12$LQv3c1yqBWVHxkd0LQ1Cr.pRJtv/g9DnXsyIH8BQZK/NQJhJgdaO2', -- Admin@SevaSetu1
    'admin',
    'Maharashtra',
    'en',
    TRUE,
    TRUE
);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

CREATE OR REPLACE VIEW v_user_stats AS
SELECT
    u.id,
    u.name,
    u.email,
    u.state,
    u.role,
    COUNT(DISTINCT q.id)  AS total_queries,
    COUNT(DISTINCT d.id)  AS total_documents,
    COUNT(DISTINCT us.id) AS schemes_checked,
    u.created_at
FROM users u
LEFT JOIN query_history q  ON q.user_id  = u.id
LEFT JOIN documents d      ON d.user_id  = u.id
LEFT JOIN user_schemes us  ON us.user_id = u.id
GROUP BY u.id;


CREATE OR REPLACE VIEW v_query_analytics AS
SELECT
    DATE(created_at)           AS query_date,
    category,
    language,
    COUNT(*)                   AS total,
    AVG(confidence)            AS avg_confidence,
    SUM(is_bookmarked)         AS bookmarked
FROM query_history
GROUP BY DATE(created_at), category, language
ORDER BY query_date DESC;
