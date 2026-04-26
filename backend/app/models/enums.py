from enum import StrEnum


class Industry(StrEnum):
    FINANCIAL_SERVICES = "financial_services"
    HEALTHCARE = "healthcare"
    RETAIL_ECOMMERCE = "retail_ecommerce"
    EDUCATION = "education"
    LOGISTICS = "logistics"
    HOSPITALITY = "hospitality"
    REAL_ESTATE = "real_estate"
    SAAS_TECH = "saas_tech"
    LEGAL = "legal"
    MARKETING = "marketing"
    MANUFACTURING = "manufacturing"
    NONPROFIT = "nonprofit"
    OTHER = "other"


class UseCase(StrEnum):
    CUSTOMER_SUPPORT = "customer_support"
    TECHNICAL_SUPPORT = "technical_support"
    SALES_INQUIRIES = "sales_inquiries"
    BOOKINGS_RESERVATIONS = "bookings_reservations"
    LOGISTICS_TRACKING = "logistics_tracking"
    INTERNAL_OPS = "internal_ops"
    OTHER = "other"


class Urgency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VolumePeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DiscoveryChannel(StrEnum):
    CONFERENCE = "conference"
    REFERRAL = "referral"
    GOOGLE_SEARCH = "google_search"
    LINKEDIN = "linkedin"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    FORUM = "forum"
    TRADE_FAIR = "trade_fair"
    OTHER = "other"


class PersonalizationConcern(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DataSensitivity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CustomerSegment(StrEnum):
    SMB = "smb"
    MIDMARKET = "midmarket"
    ENTERPRISE = "enterprise"
    UNKNOWN = "unknown"
