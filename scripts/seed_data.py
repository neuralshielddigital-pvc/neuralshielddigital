from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.admin_user import AdminUser
from app.models.blog_category import BlogCategory
from app.models.blog_post import BlogPost
from app.models.page_seo import PageSEO
from app.models.product import Product
from app.models.service import Service
from app.models.testimonial import Testimonial
from app.services.auth_service import AdminAuthenticationService


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


SERVICES = [
    {
        "name": "AI Consulting",
        "slug": "ai-consulting",
        "tagline": "Strategy-first AI execution for serious business outcomes.",
        "short_description": "Advisory and implementation planning for organizations adopting AI, LLMs, analytics, and automation across products and operations.",
        "full_description": "NeuralShield Digital helps leadership teams translate AI ambition into a practical roadmap. We work on use-case prioritization, delivery sequencing, architecture direction, cost-risk decisions, and transformation planning so internal teams can move from experimentation to measurable execution.",
        "icon_name": "radar",
        "hero_title": "AI strategy with delivery discipline built in.",
        "hero_subtitle": "We help teams identify where AI creates real leverage, then design the right operating model, architecture, and roadmap to make it happen.",
        "cta_label": "Book Strategic Consultation",
        "cta_url": "/book-consultation",
        "display_order": 1,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "Python Engineering",
        "slug": "python-engineering",
        "tagline": "Modern backend and automation systems built on Python.",
        "short_description": "Production-grade Python engineering for APIs, automation, internal platforms, data systems, and AI-enabled applications.",
        "full_description": "We design and implement maintainable Python systems using clean architecture, API-first backend development, workflow automation, asynchronous processing, and cloud-ready deployment patterns. This service supports both custom software initiatives and AI product delivery.",
        "icon_name": "code",
        "hero_title": "Python systems that stay maintainable as they scale.",
        "hero_subtitle": "From internal tools to public-facing platforms, we build reliable Python foundations for modern technology delivery.",
        "cta_label": "Discuss a Python Build",
        "cta_url": "/contact",
        "display_order": 2,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "Machine Learning Engineering",
        "slug": "machine-learning-engineering",
        "tagline": "Applied ML systems designed for measurable business impact.",
        "short_description": "End-to-end machine learning delivery for prediction, classification, anomaly detection, recommendation, and optimization use cases.",
        "full_description": "NeuralShield Digital builds machine learning systems that align model quality with operational usability. We support data preparation, feature design, experimentation, validation, deployment planning, and integration into business workflows so ML becomes a working capability instead of a research artifact.",
        "icon_name": "activity",
        "hero_title": "Applied machine learning built for production reality.",
        "hero_subtitle": "We create ML pipelines and applications that are testable, monitorable, and ready to support real decisions.",
        "cta_label": "Explore ML Solutions",
        "cta_url": "/book-consultation",
        "display_order": 3,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "NLP and Document Intelligence",
        "slug": "nlp-and-document-intelligence",
        "tagline": "Turn language, documents, and knowledge into usable systems.",
        "short_description": "NLP workflows for extraction, classification, summarization, semantic search, knowledge systems, and document-heavy operations.",
        "full_description": "We implement natural language processing and document intelligence systems that help organizations process unstructured text at scale. Typical use cases include intake automation, contract analysis, document routing, knowledge search, customer communication enrichment, and internal research acceleration.",
        "icon_name": "file-text",
        "hero_title": "NLP that solves real operational problems.",
        "hero_subtitle": "We transform text-heavy workflows into structured, searchable, and automation-ready business systems.",
        "cta_label": "Start an NLP Discovery",
        "cta_url": "/contact",
        "display_order": 4,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "DLP and Intelligent Data Protection",
        "slug": "dlp-and-intelligent-data-protection",
        "tagline": "Data protection workflows supported by AI and policy-aware automation.",
        "short_description": "DLP-aligned systems for sensitive data discovery, classification, workflow controls, monitoring, and secure AI enablement.",
        "full_description": "We help organizations design data protection workflows that support secure automation and AI adoption. This includes document classification, policy-aware processing, risk flagging, controlled access patterns, and operational safeguards for teams handling regulated or sensitive business information.",
        "icon_name": "shield",
        "hero_title": "Security-aware AI workflows for sensitive environments.",
        "hero_subtitle": "Our DLP-oriented solutions combine automation, visibility, and governance so teams can move faster without compromising control.",
        "cta_label": "Discuss Secure AI Enablement",
        "cta_url": "/book-consultation",
        "display_order": 5,
        "is_active": True,
        "is_featured": False,
    },
    {
        "name": "LLM and Generative AI Solutions",
        "slug": "llm-and-generative-ai-solutions",
        "tagline": "Enterprise-ready generative AI with trust, control, and usefulness.",
        "short_description": "LLM-powered assistants, RAG systems, generative workflows, copilots, and domain-specific knowledge tools.",
        "full_description": "We build generative AI systems with the guardrails and engineering depth needed for production use. Services cover architecture design, retrieval pipelines, prompt systems, evaluation patterns, human-in-the-loop workflows, and business process integration for practical LLM adoption.",
        "icon_name": "sparkles",
        "hero_title": "Generative AI that is actually usable in the real world.",
        "hero_subtitle": "From internal copilots to domain assistants, we design LLM systems that are helpful, observable, and controllable.",
        "cta_label": "Plan an LLM Project",
        "cta_url": "/book-consultation",
        "display_order": 6,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "Agentic AI and Automation",
        "slug": "agentic-ai-and-automation",
        "tagline": "Connected AI workflows that coordinate tools, context, and action.",
        "short_description": "Agentic orchestration and business automation for internal operations, multi-step workflows, research tasks, and process acceleration.",
        "full_description": "NeuralShield Digital designs agentic systems that combine AI reasoning, external tools, workflow logic, and human oversight. This supports use cases such as intake processing, research assistance, knowledge operations, customer support acceleration, and internal execution copilots.",
        "icon_name": "cpu",
        "hero_title": "Automation that goes beyond static rules.",
        "hero_subtitle": "We build intelligent workflows that can interpret context, call tools, and move work forward with the right level of control.",
        "cta_label": "Automate a Process",
        "cta_url": "/contact",
        "display_order": 7,
        "is_active": True,
        "is_featured": True,
    },
    {
        "name": "Computer Vision Systems",
        "slug": "computer-vision-systems",
        "tagline": "Visual intelligence for analysis, inspection, and monitoring.",
        "short_description": "Computer vision solutions for document vision, classification, object detection, quality checks, and visual workflow automation.",
        "full_description": "We help businesses deploy vision systems where image and video understanding can improve speed, quality, and accuracy. Engagements often include document processing, defect detection, image indexing, inspection workflows, and operational monitoring use cases.",
        "icon_name": "eye",
        "hero_title": "Computer vision built for practical workflows.",
        "hero_subtitle": "From visual inspection to document analysis, we design vision pipelines that fit operational reality and business goals.",
        "cta_label": "Explore Vision Use Cases",
        "cta_url": "/book-consultation",
        "display_order": 8,
        "is_active": True,
        "is_featured": False,
    },
    {
        "name": "MLOps and DevOps Enablement",
        "slug": "mlops-and-devops-enablement",
        "tagline": "Operational foundations for dependable AI and software delivery.",
        "short_description": "MLOps and DevOps delivery covering pipelines, release automation, observability, environments, and lifecycle management.",
        "full_description": "We strengthen the engineering backbone behind AI and software systems by improving deployment workflows, environment design, CI/CD, model operations, logging, monitoring, and recovery practices. The goal is to make delivery faster, safer, and easier to operate over time.",
        "icon_name": "server",
        "hero_title": "Operational maturity for teams building serious systems.",
        "hero_subtitle": "We bring release discipline, observability, and maintainability into both AI platforms and custom software delivery.",
        "cta_label": "Improve Delivery Operations",
        "cta_url": "/contact",
        "display_order": 9,
        "is_active": True,
        "is_featured": False,
    },
    {
        "name": "Data Science and Decision Intelligence",
        "slug": "data-science-and-decision-intelligence",
        "tagline": "Data-driven systems that clarify what matters and why.",
        "short_description": "Advanced analytics, forecasting, experimentation, and decision-support workflows for organizations scaling with data.",
        "full_description": "We help teams turn fragmented data into decision-ready systems through analytics models, dashboards, experimentation support, and intelligent reporting. This service fits companies that need practical insight generation before, during, or alongside AI adoption.",
        "icon_name": "bar-chart-3",
        "hero_title": "Data science that supports action, not just reporting.",
        "hero_subtitle": "We design insight pipelines and analytics workflows that improve planning, prioritization, and operational visibility.",
        "cta_label": "Talk to a Data Science Partner",
        "cta_url": "/contact",
        "display_order": 10,
        "is_active": True,
        "is_featured": False,
    },
]

PRODUCTS = [
    {
        "name": "Neural Automation Suite",
        "slug": "neural-automation-suite",
        "tagline": "A modular platform for AI-assisted business workflow orchestration.",
        "short_description": "Automation platform for internal operations, document workflows, approvals, task routing, and AI-assisted execution.",
        "full_description": "Neural Automation Suite helps organizations streamline work across departments by combining configurable workflow logic, integrations, human approvals, and AI-powered decision support. It is well-suited to document-centric operations, operational service teams, and organizations modernizing internal execution.",
        "product_type": "platform",
        "status": "published",
        "website_url": "https://neuralshielddigital.com/products/neural-automation-suite",
        "cta_label": "Request a Demo",
        "cta_url": "/contact",
        "pricing_summary": "Custom enterprise pricing",
        "display_order": 1,
        "is_featured": True,
        "published_at": utc_now(),
    },
    {
        "name": "Neural Insight Engine",
        "slug": "neural-insight-engine",
        "tagline": "An AI-enabled analytics layer for operational visibility and smarter decisions.",
        "short_description": "Decision-support product for reporting, KPI monitoring, operational insight generation, and business intelligence workflows.",
        "full_description": "Neural Insight Engine combines analytics pipelines, intelligent summarization, and role-based visibility to help teams understand performance faster. It supports leadership reporting, operations review, and insight generation for organizations that want more than static dashboards.",
        "product_type": "analytics",
        "status": "published",
        "website_url": "https://neuralshielddigital.com/products/neural-insight-engine",
        "cta_label": "Explore the Platform",
        "cta_url": "/book-consultation",
        "pricing_summary": "Consultation-led implementation",
        "display_order": 2,
        "is_featured": True,
        "published_at": utc_now(),
    },
    {
        "name": "Neural Knowledge Copilot",
        "slug": "neural-knowledge-copilot",
        "tagline": "A domain-aware assistant for search, Q&A, and secure internal knowledge workflows.",
        "short_description": "LLM and retrieval-powered knowledge assistant for internal documentation, SOPs, customer operations, and team enablement.",
        "full_description": "Neural Knowledge Copilot gives teams a trusted interface for internal knowledge access using retrieval, workflow safeguards, and source-aware answers. It is designed for operations, support, enablement, and knowledge management environments where reliability and security matter.",
        "product_type": "assistant",
        "status": "published",
        "website_url": "https://neuralshielddigital.com/products/neural-knowledge-copilot",
        "cta_label": "See Product Fit",
        "cta_url": "/contact",
        "pricing_summary": "Custom rollout by team size",
        "display_order": 3,
        "is_featured": False,
        "published_at": utc_now(),
    },
]

BLOG_CATEGORIES = [
    {
        "name": "AI Strategy",
        "slug": "ai-strategy",
        "description": "Practical guidance on AI adoption, operating models, use-case prioritization, and transformation planning.",
    },
    {
        "name": "Generative AI",
        "slug": "generative-ai",
        "description": "LLMs, retrieval systems, prompt architecture, AI assistants, and responsible GenAI delivery.",
    },
    {
        "name": "Machine Learning",
        "slug": "machine-learning",
        "description": "Applied machine learning, model design, experimentation, and delivery patterns.",
    },
    {
        "name": "MLOps and DevOps",
        "slug": "mlops-and-devops",
        "description": "Infrastructure, CI/CD, observability, deployment systems, and operating discipline for modern AI teams.",
    },
]

BLOG_POSTS = [
    {
        "title": "How to Move From AI Curiosity to an Executable Delivery Roadmap",
        "slug": "ai-curiosity-to-executable-delivery-roadmap",
        "category_slug": "ai-strategy",
        "excerpt": "A practical framework for organizations that want to prioritize AI opportunities, align stakeholders, and turn early enthusiasm into a real delivery plan.",
        "featured_image": "",
        "content_markdown": """AI programs often lose momentum because the initial excitement is not matched by a clear operating model. Teams explore ideas, run ad hoc pilots, and still struggle to decide what should be built first.\n\nA strong roadmap starts with business friction, not model novelty. The best early initiatives reduce manual load, improve response speed, or increase decision quality in places where the team already understands the workflow.\n\nNeuralShield Digital recommends a roadmap structure built around measurable value, delivery feasibility, data readiness, and organizational ownership. That approach helps teams move from scattered experimentation to a sequence of projects that can actually be delivered.""",
        "content_html": """<p>AI programs often lose momentum because the initial excitement is not matched by a clear operating model. Teams explore ideas, run ad hoc pilots, and still struggle to decide what should be built first.</p><p>A strong roadmap starts with business friction, not model novelty. The best early initiatives reduce manual load, improve response speed, or increase decision quality in places where the team already understands the workflow.</p><p>NeuralShield Digital recommends a roadmap structure built around measurable value, delivery feasibility, data readiness, and organizational ownership. That approach helps teams move from scattered experimentation to a sequence of projects that can actually be delivered.</p>""",
        "status": "published",
        "is_featured": True,
        "published_at": utc_now(),
    },
    {
        "title": "Designing LLM Systems With Retrieval, Guardrails, and Operational Trust",
        "slug": "designing-llm-systems-with-retrieval-guardrails-and-operational-trust",
        "category_slug": "generative-ai",
        "excerpt": "What teams should think about when moving beyond prompt demos into production-grade LLM systems.",
        "featured_image": "",
        "content_markdown": """Prompting alone is not an enterprise architecture. Useful LLM systems need retrieval quality, access controls, observability, evaluation loops, fallback behavior, and clear human escalation points.\n\nThe strongest implementations treat generative AI as a product surface supported by engineering discipline. That means source-grounded responses, transparent boundaries, reliable tool integrations, and quality measurement that extends beyond anecdotal testing.\n\nWhen retrieval, safeguards, and workflow design are handled well, LLM systems become much more dependable and much more valuable to the business.""",
        "content_html": """<p>Prompting alone is not an enterprise architecture. Useful LLM systems need retrieval quality, access controls, observability, evaluation loops, fallback behavior, and clear human escalation points.</p><p>The strongest implementations treat generative AI as a product surface supported by engineering discipline. That means source-grounded responses, transparent boundaries, reliable tool integrations, and quality measurement that extends beyond anecdotal testing.</p><p>When retrieval, safeguards, and workflow design are handled well, LLM systems become much more dependable and much more valuable to the business.</p>""",
        "status": "published",
        "is_featured": True,
        "published_at": utc_now(),
    },
    {
        "title": "What Good Machine Learning Delivery Looks Like Outside the Lab",
        "slug": "what-good-machine-learning-delivery-looks-like-outside-the-lab",
        "category_slug": "machine-learning",
        "excerpt": "A practical look at how ML projects succeed when they are designed around workflows, not just models.",
        "featured_image": "",
        "content_markdown": """A model with promising offline results is only the beginning. In production, success depends on feature availability, process fit, feedback loops, monitoring, and whether the outputs can be trusted by the people using them.\n\nThe most effective machine learning systems are shaped by operational context from the start. Teams need to know where predictions enter the workflow, who acts on them, how error is handled, and what happens when data quality changes.\n\nThat is why applied ML delivery should be treated as a systems problem, not just a modeling problem.""",
        "content_html": """<p>A model with promising offline results is only the beginning. In production, success depends on feature availability, process fit, feedback loops, monitoring, and whether the outputs can be trusted by the people using them.</p><p>The most effective machine learning systems are shaped by operational context from the start. Teams need to know where predictions enter the workflow, who acts on them, how error is handled, and what happens when data quality changes.</p><p>That is why applied ML delivery should be treated as a systems problem, not just a modeling problem.</p>""",
        "status": "published",
        "is_featured": False,
        "published_at": utc_now(),
    },
    {
        "title": "Why MLOps and DevOps Need to Be Designed Together",
        "slug": "why-mlops-and-devops-need-to-be-designed-together",
        "category_slug": "mlops-and-devops",
        "excerpt": "Reliable AI delivery depends on more than model packaging. It needs shared operational discipline across engineering and ML teams.",
        "featured_image": "",
        "content_markdown": """Many organizations treat MLOps as a specialist add-on that comes after model development. In practice, deployment quality depends on the same fundamentals that shape mature software delivery: environments, release workflows, observability, rollback planning, and clear ownership.\n\nWhen DevOps and MLOps are designed separately, teams inherit avoidable friction. Release pipelines become inconsistent, monitoring becomes fragmented, and operational responsibility gets blurred.\n\nBringing the two together earlier helps organizations ship AI systems with more confidence and less rework.""",
        "content_html": """<p>Many organizations treat MLOps as a specialist add-on that comes after model development. In practice, deployment quality depends on the same fundamentals that shape mature software delivery: environments, release workflows, observability, rollback planning, and clear ownership.</p><p>When DevOps and MLOps are designed separately, teams inherit avoidable friction. Release pipelines become inconsistent, monitoring becomes fragmented, and operational responsibility gets blurred.</p><p>Bringing the two together earlier helps organizations ship AI systems with more confidence and less rework.</p>""",
        "status": "published",
        "is_featured": False,
        "published_at": utc_now(),
    },
]

TESTIMONIALS = [
    {
        "client_name": "Aarav Mehta",
        "company_name": "FinStream Ops",
        "designation": "Operations Director",
        "testimonial_text": "NeuralShield Digital helped us turn a vague automation agenda into a structured AI roadmap with clear technical priorities and realistic execution steps.",
        "rating": 5,
        "is_featured": True,
        "display_order": 1,
        "source_url": "https://neuralshielddigital.com",
        "is_active": True,
    },
    {
        "client_name": "Priya Raman",
        "company_name": "VisionGrid Labs",
        "designation": "Product Lead",
        "testimonial_text": "Their team brought clarity to our LLM architecture, retrieval design, and rollout planning. The engagement felt strategic and deeply technical at the same time.",
        "rating": 5,
        "is_featured": True,
        "display_order": 2,
        "source_url": "https://neuralshielddigital.com",
        "is_active": True,
    },
    {
        "client_name": "Nikhil Sethi",
        "company_name": "DataHarbor Systems",
        "designation": "CTO",
        "testimonial_text": "We needed a partner that understood both machine learning and production engineering. NeuralShield Digital delivered a plan we could actually execute with confidence.",
        "rating": 5,
        "is_featured": False,
        "display_order": 3,
        "source_url": "https://neuralshielddigital.com",
        "is_active": True,
    },
]

PAGE_SEO = [
    {
        "page_key": "home",
        "page_type": "page",
        "object_id": None,
        "page_path": "/",
        "meta_title": "NeuralShield Digital | AI Consulting, ML Engineering, Automation, and AI Products",
        "meta_description": "NeuralShield Digital builds enterprise AI systems, LLM solutions, machine learning platforms, automation workflows, and custom software products.",
        "meta_keywords": "AI consulting, Python development, machine learning, NLP, DLP, LLM, generative AI, agentic AI, computer vision, MLOps, DevOps, data science",
        "canonical_url": "https://neuralshielddigital.com/",
        "robots": "index,follow",
        "og_title": "NeuralShield Digital",
        "og_description": "AI systems, automation, machine learning, and software delivery for modern businesses.",
        "og_image": "",
        "twitter_title": "NeuralShield Digital",
        "twitter_description": "AI systems, automation, machine learning, and software delivery for modern businesses.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"Organization","name":"NeuralShield Digital","url":"https://neuralshielddigital.com"}',
    },
    {
        "page_key": "about",
        "page_type": "page",
        "object_id": None,
        "page_path": "/about",
        "meta_title": "About NeuralShield Digital",
        "meta_description": "Learn how NeuralShield Digital helps organizations deliver AI strategy, engineering, automation, and modern digital products.",
        "meta_keywords": "about NeuralShield Digital, AI company, technology consulting",
        "canonical_url": "https://neuralshielddigital.com/about",
        "robots": "index,follow",
        "og_title": "About NeuralShield Digital",
        "og_description": "A practical AI and technology partner for strategy, systems, and execution.",
        "og_image": "",
        "twitter_title": "About NeuralShield Digital",
        "twitter_description": "A practical AI and technology partner for strategy, systems, and execution.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"AboutPage","name":"About NeuralShield Digital"}',
    },
    {
        "page_key": "services",
        "page_type": "page",
        "object_id": None,
        "page_path": "/services",
        "meta_title": "AI and Technology Services | NeuralShield Digital",
        "meta_description": "Explore AI consulting, Python engineering, ML, NLP, DLP, generative AI, agentic automation, computer vision, MLOps, DevOps, and data science services.",
        "meta_keywords": "AI services, Python services, ML engineering, NLP services, MLOps consulting, generative AI consulting",
        "canonical_url": "https://neuralshielddigital.com/services",
        "robots": "index,follow",
        "og_title": "NeuralShield Digital Services",
        "og_description": "Enterprise-focused AI, engineering, automation, and software services.",
        "og_image": "",
        "twitter_title": "NeuralShield Digital Services",
        "twitter_description": "Enterprise-focused AI, engineering, automation, and software services.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"CollectionPage","name":"Services"}',
    },
    {
        "page_key": "products",
        "page_type": "page",
        "object_id": None,
        "page_path": "/products",
        "meta_title": "AI Products and Platforms | NeuralShield Digital",
        "meta_description": "Discover AI-enabled products, workflow automation platforms, and decision-support systems built by NeuralShield Digital.",
        "meta_keywords": "AI products, automation platform, AI assistant, analytics platform",
        "canonical_url": "https://neuralshielddigital.com/products",
        "robots": "index,follow",
        "og_title": "NeuralShield Digital Products",
        "og_description": "AI products and platforms for modern business operations.",
        "og_image": "",
        "twitter_title": "NeuralShield Digital Products",
        "twitter_description": "AI products and platforms for modern business operations.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"CollectionPage","name":"Products"}',
    },
    {
        "page_key": "blog",
        "page_type": "page",
        "object_id": None,
        "page_path": "/blog",
        "meta_title": "AI Insights and Engineering Articles | NeuralShield Digital",
        "meta_description": "Insights on AI strategy, generative AI, machine learning, MLOps, DevOps, automation, and applied software delivery.",
        "meta_keywords": "AI blog, generative AI insights, machine learning articles, MLOps blog",
        "canonical_url": "https://neuralshielddigital.com/blog",
        "robots": "index,follow",
        "og_title": "NeuralShield Digital Blog",
        "og_description": "Applied insight on AI, engineering, and digital delivery.",
        "og_image": "",
        "twitter_title": "NeuralShield Digital Blog",
        "twitter_description": "Applied insight on AI, engineering, and digital delivery.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"Blog","name":"NeuralShield Digital Blog"}',
    },
    {
        "page_key": "contact",
        "page_type": "page",
        "object_id": None,
        "page_path": "/contact",
        "meta_title": "Contact NeuralShield Digital",
        "meta_description": "Contact NeuralShield Digital to discuss AI consulting, Python development, generative AI, machine learning, and automation initiatives.",
        "meta_keywords": "contact AI company, contact NeuralShield Digital",
        "canonical_url": "https://neuralshielddigital.com/contact",
        "robots": "index,follow",
        "og_title": "Contact NeuralShield Digital",
        "og_description": "Start a conversation about AI, automation, and software delivery.",
        "og_image": "",
        "twitter_title": "Contact NeuralShield Digital",
        "twitter_description": "Start a conversation about AI, automation, and software delivery.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"ContactPage","name":"Contact NeuralShield Digital"}',
    },
    {
        "page_key": "book-consultation",
        "page_type": "page",
        "object_id": None,
        "page_path": "/book-consultation",
        "meta_title": "Book an AI Consultation | NeuralShield Digital",
        "meta_description": "Book a consultation with NeuralShield Digital to discuss AI strategy, LLM products, automation, ML systems, and technical delivery.",
        "meta_keywords": "book AI consultation, AI strategy call, NeuralShield Digital consultation",
        "canonical_url": "https://neuralshielddigital.com/book-consultation",
        "robots": "index,follow",
        "og_title": "Book an AI Consultation",
        "og_description": "Schedule a strategy or technical consultation with NeuralShield Digital.",
        "og_image": "",
        "twitter_title": "Book an AI Consultation",
        "twitter_description": "Schedule a strategy or technical consultation with NeuralShield Digital.",
        "twitter_image": "",
        "schema_json": '{"@context":"https://schema.org","@type":"Service","name":"Consultation Booking"}',
    },
]


def get_or_create_admin(session: Session) -> AdminUser:
    settings = get_settings()
    admin = session.scalar(select(AdminUser).order_by(AdminUser.id.asc()))
    if admin:
        return admin
    return AdminAuthenticationService(session).create_admin(
        email=str(settings.admin_default_email),
        full_name="NeuralShield Digital Admin",
        password=settings.admin_default_password,
        role="super_admin",
        is_active=True,
    )


def seed_services(session: Session) -> list[Service]:
    items: list[Service] = []
    for data in SERVICES:
        existing = session.scalar(select(Service).where(Service.slug == data["slug"]))
        if existing:
            items.append(existing)
            continue
        item = Service(**data)
        session.add(item)
        session.flush()
        items.append(item)
    return items


def seed_products(session: Session) -> list[Product]:
    items: list[Product] = []
    for data in PRODUCTS:
        existing = session.scalar(select(Product).where(Product.slug == data["slug"]))
        if existing:
            items.append(existing)
            continue
        item = Product(**data)
        session.add(item)
        session.flush()
        items.append(item)
    return items


def seed_blog_categories(session: Session) -> dict[str, BlogCategory]:
    items: dict[str, BlogCategory] = {}
    for data in BLOG_CATEGORIES:
        existing = session.scalar(select(BlogCategory).where(BlogCategory.slug == data["slug"]))
        if existing:
            items[data["slug"]] = existing
            continue
        category = BlogCategory(
            name=data["name"],
            slug=data["slug"],
            description=data["description"],
        )
        session.add(category)
        session.flush()
        items[data["slug"]] = category
    return items


def seed_blog_posts(
    session: Session,
    *,
    author: AdminUser,
    categories: dict[str, BlogCategory],
) -> list[BlogPost]:
    items: list[BlogPost] = []
    for data in BLOG_POSTS:
        existing = session.scalar(select(BlogPost).where(BlogPost.slug == data["slug"]))
        if existing:
            items.append(existing)
            continue

        category = categories[data["category_slug"]]
        post = BlogPost(
            title=data["title"],
            slug=data["slug"],
            excerpt=data["excerpt"],
            featured_image=data["featured_image"],
            content_markdown=data["content_markdown"],
            content_html=data["content_html"],
            status=data["status"],
            is_featured=data["is_featured"],
            published_at=data["published_at"],
            category_id=category.id,
            author_id=author.id,
        )
        session.add(post)
        session.flush()
        items.append(post)
    return items


def seed_testimonials(session: Session) -> list[Testimonial]:
    items: list[Testimonial] = []
    for data in TESTIMONIALS:
        existing = session.scalar(
            select(Testimonial).where(
                Testimonial.client_name == data["client_name"],
                Testimonial.company_name == data["company_name"],
            )
        )
        if existing:
            items.append(existing)
            continue
        testimonial = Testimonial(**data)
        session.add(testimonial)
        session.flush()
        items.append(testimonial)
    return items


def seed_page_seo(
    session: Session,
    *,
    services: list[Service],
    products: list[Product],
    posts: list[BlogPost],
) -> list[PageSEO]:
    entries = list(PAGE_SEO)

    for service in services:
        entries.append(
            {
                "page_key": f"service:{service.slug}",
                "page_type": "service",
                "object_id": service.id,
                "page_path": f"/services/{service.slug}",
                "meta_title": f"{service.name} | NeuralShield Digital",
                "meta_description": service.short_description,
                "meta_keywords": service.name,
                "canonical_url": f"https://neuralshielddigital.com/services/{service.slug}",
                "robots": "index,follow",
                "og_title": service.name,
                "og_description": service.short_description,
                "og_image": "",
                "twitter_title": service.name,
                "twitter_description": service.short_description,
                "twitter_image": "",
                "schema_json": f'{{"@context":"https://schema.org","@type":"Service","name":"{service.name}"}}',
            }
        )

    for product in products:
        entries.append(
            {
                "page_key": f"product:{product.slug}",
                "page_type": "product",
                "object_id": product.id,
                "page_path": f"/products/{product.slug}",
                "meta_title": f"{product.name} | NeuralShield Digital",
                "meta_description": product.short_description,
                "meta_keywords": product.name,
                "canonical_url": f"https://neuralshielddigital.com/products/{product.slug}",
                "robots": "index,follow",
                "og_title": product.name,
                "og_description": product.short_description,
                "og_image": "",
                "twitter_title": product.name,
                "twitter_description": product.short_description,
                "twitter_image": "",
                "schema_json": f'{{"@context":"https://schema.org","@type":"Product","name":"{product.name}"}}',
            }
        )

    for post in posts:
        entries.append(
            {
                "page_key": f"blog:{post.slug}",
                "page_type": "blog_post",
                "object_id": post.id,
                "page_path": f"/blog/{post.slug}",
                "meta_title": post.title,
                "meta_description": post.excerpt or post.title,
                "meta_keywords": "AI blog, machine learning, generative AI, automation, MLOps",
                "canonical_url": f"https://neuralshielddigital.com/blog/{post.slug}",
                "robots": "index,follow",
                "og_title": post.title,
                "og_description": post.excerpt or post.title,
                "og_image": "",
                "twitter_title": post.title,
                "twitter_description": post.excerpt or post.title,
                "twitter_image": "",
                "schema_json": f'{{"@context":"https://schema.org","@type":"Article","headline":"{post.title}"}}',
            }
        )

    items: list[PageSEO] = []
    for data in entries:
        existing = session.scalar(select(PageSEO).where(PageSEO.page_key == data["page_key"]))
        if existing:
            items.append(existing)
            continue
        seo_entry = PageSEO(**data)
        session.add(seo_entry)
        session.flush()
        items.append(seo_entry)
    return items


def main() -> None:
    session = SessionLocal()
    try:
        admin = get_or_create_admin(session)
        services = seed_services(session)
        products = seed_products(session)
        categories = seed_blog_categories(session)
        posts = seed_blog_posts(session, author=admin, categories=categories)
        testimonials = seed_testimonials(session)
        seo_entries = seed_page_seo(
            session,
            services=services,
            products=products,
            posts=posts,
        )
        session.commit()

        print(
            "Seed complete: "
            f"{len(services)} services, "
            f"{len(products)} products, "
            f"{len(categories)} blog categories, "
            f"{len(posts)} blog posts, "
            f"{len(testimonials)} testimonials, "
            f"{len(seo_entries)} SEO entries."
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
