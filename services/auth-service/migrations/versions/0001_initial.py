"""initial auth schema"""
from alembic import op
import sqlalchemy as sa
revision="0001_auth"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("users",sa.Column("id",sa.String(36),primary_key=True),sa.Column("email",sa.String(255),nullable=False),sa.Column("full_name",sa.String(120),nullable=False),sa.Column("password_hash",sa.String(255),nullable=False),sa.Column("role",sa.String(20),nullable=False),sa.Column("active",sa.Boolean(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_users_email","users",["email"],unique=True); op.create_index("ix_users_role","users",["role"])
    op.create_table("auth_audit",sa.Column("id",sa.String(36),primary_key=True),sa.Column("actor_user_id",sa.String(36),nullable=True),sa.Column("action",sa.String(80),nullable=False),sa.Column("resource_id",sa.String(36),nullable=False),sa.Column("metadata_json",sa.Text(),nullable=False),sa.Column("timestamp",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_auth_audit_timestamp","auth_audit",["timestamp"]); op.create_index("ix_auth_audit_action","auth_audit",["action"])
def downgrade():
    op.drop_table("auth_audit"); op.drop_table("users")
