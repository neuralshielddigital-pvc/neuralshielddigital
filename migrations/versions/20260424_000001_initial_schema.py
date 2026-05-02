"""initial schema

Revision ID: 20260424_000001
Revises:
Create Date: 2026-04-24 18:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260424_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="super_admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_ip", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_admin_users_email"),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=False)

    op.create_table(
        "blog_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_blog_categories_name"),
        sa.UniqueConstraint("slug", name="uq_blog_categories_slug"),
    )
    op.create_index("ix_blog_categories_slug", "blog_categories", ["slug"], unique=False)

    op.create_table(
        "contact_leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("service_interest", sa.String(length=255), nullable=True),
        sa.Column("source_page", sa.String(length=255), nullable=False, server_default="/contact"),
        sa.Column("lead_source", sa.String(length=100), nullable=False, server_default="website"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="normal"),
        sa.Column("budget_range", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("assigned_admin_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["assigned_admin_id"], ["admin_users.id"], name="fk_contact_leads_assigned_admin_id_admin_users", ondelete="SET NULL"),
    )
    op.create_index("ix_contact_leads_assigned_admin_id", "contact_leads", ["assigned_admin_id"], unique=False)
    op.create_index("ix_contact_leads_email", "contact_leads", ["email"], unique=False)
    op.create_index("ix_contact_leads_full_name", "contact_leads", ["full_name"], unique=False)
    op.create_index("ix_contact_leads_status", "contact_leads", ["status"], unique=False)

    op.create_table(
        "page_seo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("page_key", sa.String(length=100), nullable=False),
        sa.Column("page_type", sa.String(length=50), nullable=False),
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("page_path", sa.String(length=255), nullable=False),
        sa.Column("meta_title", sa.String(length=255), nullable=True),
        sa.Column("meta_description", sa.String(length=500), nullable=True),
        sa.Column("meta_keywords", sa.String(length=500), nullable=True),
        sa.Column("canonical_url", sa.String(length=500), nullable=True),
        sa.Column("robots", sa.String(length=100), nullable=False, server_default="index,follow"),
        sa.Column("og_title", sa.String(length=255), nullable=True),
        sa.Column("og_description", sa.String(length=500), nullable=True),
        sa.Column("og_image", sa.String(length=500), nullable=True),
        sa.Column("twitter_title", sa.String(length=255), nullable=True),
        sa.Column("twitter_description", sa.String(length=500), nullable=True),
        sa.Column("twitter_image", sa.String(length=500), nullable=True),
        sa.Column("schema_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("page_key", name="uq_page_seo_page_key"),
        sa.UniqueConstraint("page_path", name="uq_page_seo_page_path"),
        sa.UniqueConstraint("page_type", "object_id", name="uq_page_seo_page_type_object_id"),
    )
    op.create_index("ix_page_seo_object_id", "page_seo", ["object_id"], unique=False)
    op.create_index("ix_page_seo_page_key", "page_seo", ["page_key"], unique=False)
    op.create_index("ix_page_seo_page_type", "page_seo", ["page_type"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("tagline", sa.String(length=255), nullable=True),
        sa.Column("short_description", sa.String(length=500), nullable=False),
        sa.Column("full_description", sa.Text(), nullable=False),
        sa.Column("product_type", sa.String(length=100), nullable=False, server_default="platform"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("cta_label", sa.String(length=100), nullable=True),
        sa.Column("cta_url", sa.String(length=255), nullable=True),
        sa.Column("pricing_summary", sa.String(length=255), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_products_name"),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
    )
    op.create_index("ix_products_slug", "products", ["slug"], unique=False)
    op.create_index("ix_products_status", "products", ["status"], unique=False)
    op.create_index("ix_products_is_featured", "products", ["is_featured"], unique=False)

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("tagline", sa.String(length=255), nullable=True),
        sa.Column("short_description", sa.String(length=500), nullable=False),
        sa.Column("full_description", sa.Text(), nullable=False),
        sa.Column("icon_name", sa.String(length=100), nullable=True),
        sa.Column("hero_title", sa.String(length=255), nullable=True),
        sa.Column("hero_subtitle", sa.Text(), nullable=True),
        sa.Column("cta_label", sa.String(length=100), nullable=True),
        sa.Column("cta_url", sa.String(length=255), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_services_name"),
        sa.UniqueConstraint("slug", name="uq_services_slug"),
    )
    op.create_index("ix_services_slug", "services", ["slug"], unique=False)
    op.create_index("ix_services_is_active", "services", ["is_active"], unique=False)
    op.create_index("ix_services_is_featured", "services", ["is_featured"], unique=False)

    op.create_table(
        "testimonials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_name", sa.String(length=255), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("designation", sa.String(length=255), nullable=True),
        sa.Column("testimonial_text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_testimonials_is_active", "testimonials", ["is_active"], unique=False)
    op.create_index("ix_testimonials_is_featured", "testimonials", ["is_featured"], unique=False)

    op.create_table(
        "blog_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("excerpt", sa.String(length=500), nullable=True),
        sa.Column("featured_image", sa.String(length=500), nullable=True),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("content_html", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["author_id"], ["admin_users.id"], name="fk_blog_posts_author_id_admin_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["category_id"], ["blog_categories.id"], name="fk_blog_posts_category_id_blog_categories", ondelete="SET NULL"),
        sa.UniqueConstraint("slug", name="uq_blog_posts_slug"),
    )
    op.create_index("ix_blog_posts_author_id", "blog_posts", ["author_id"], unique=False)
    op.create_index("ix_blog_posts_category_id", "blog_posts", ["category_id"], unique=False)
    op.create_index("ix_blog_posts_slug", "blog_posts", ["slug"], unique=False)
    op.create_index("ix_blog_posts_status", "blog_posts", ["status"], unique=False)
    op.create_index("ix_blog_posts_is_featured", "blog_posts", ["is_featured"], unique=False)

    op.create_table(
        "consultation_bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contact_lead_id", sa.Integer(), nullable=True),
        sa.Column("assigned_admin_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("consultation_type", sa.String(length=100), nullable=False, server_default="strategy"),
        sa.Column("preferred_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=False, server_default="Asia/Calcutta"),
        sa.Column("project_details", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("meeting_link", sa.String(length=500), nullable=True),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["assigned_admin_id"], ["admin_users.id"], name="fk_consultation_bookings_assigned_admin_id_admin_users", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["contact_lead_id"], ["contact_leads.id"], name="fk_consultation_bookings_contact_lead_id_contact_leads", ondelete="SET NULL"),
    )
    op.create_index("ix_consultation_bookings_assigned_admin_id", "consultation_bookings", ["assigned_admin_id"], unique=False)
    op.create_index("ix_consultation_bookings_contact_lead_id", "consultation_bookings", ["contact_lead_id"], unique=False)
    op.create_index("ix_consultation_bookings_email", "consultation_bookings", ["email"], unique=False)
    op.create_index("ix_consultation_bookings_full_name", "consultation_bookings", ["full_name"], unique=False)
    op.create_index("ix_consultation_bookings_status", "consultation_bookings", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_consultation_bookings_status", table_name="consultation_bookings")
    op.drop_index("ix_consultation_bookings_full_name", table_name="consultation_bookings")
    op.drop_index("ix_consultation_bookings_email", table_name="consultation_bookings")
    op.drop_index("ix_consultation_bookings_contact_lead_id", table_name="consultation_bookings")
    op.drop_index("ix_consultation_bookings_assigned_admin_id", table_name="consultation_bookings")
    op.drop_table("consultation_bookings")

    op.drop_index("ix_blog_posts_is_featured", table_name="blog_posts")
    op.drop_index("ix_blog_posts_status", table_name="blog_posts")
    op.drop_index("ix_blog_posts_slug", table_name="blog_posts")
    op.drop_index("ix_blog_posts_category_id", table_name="blog_posts")
    op.drop_index("ix_blog_posts_author_id", table_name="blog_posts")
    op.drop_table("blog_posts")

    op.drop_index("ix_testimonials_is_featured", table_name="testimonials")
    op.drop_index("ix_testimonials_is_active", table_name="testimonials")
    op.drop_table("testimonials")

    op.drop_index("ix_services_is_featured", table_name="services")
    op.drop_index("ix_services_is_active", table_name="services")
    op.drop_index("ix_services_slug", table_name="services")
    op.drop_table("services")

    op.drop_index("ix_products_is_featured", table_name="products")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_page_seo_page_type", table_name="page_seo")
    op.drop_index("ix_page_seo_page_key", table_name="page_seo")
    op.drop_index("ix_page_seo_object_id", table_name="page_seo")
    op.drop_table("page_seo")

    op.drop_index("ix_contact_leads_status", table_name="contact_leads")
    op.drop_index("ix_contact_leads_full_name", table_name="contact_leads")
    op.drop_index("ix_contact_leads_email", table_name="contact_leads")
    op.drop_index("ix_contact_leads_assigned_admin_id", table_name="contact_leads")
    op.drop_table("contact_leads")

    op.drop_index("ix_blog_categories_slug", table_name="blog_categories")
    op.drop_table("blog_categories")

    op.drop_index("ix_admin_users_email", table_name="admin_users")
    op.drop_table("admin_users")
