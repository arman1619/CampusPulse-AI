"""initial notification schema"""
from alembic import op
import sqlalchemy as sa
revision="0001_notifications";down_revision=None;branch_labels=None;depends_on=None
def upgrade():
 op.create_table("notifications",sa.Column("id",sa.String(36),primary_key=True),sa.Column("user_id",sa.String(36),nullable=False),sa.Column("message",sa.String(500),nullable=False),sa.Column("event_type",sa.String(60),nullable=False),sa.Column("resource_id",sa.String(36),nullable=True),sa.Column("read",sa.Boolean(),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("read_at",sa.DateTime(timezone=True),nullable=True));op.create_index("ix_notifications_user_read","notifications",["user_id","read"]);op.create_index("ix_notifications_created","notifications",["created_at"])
def downgrade():op.drop_table("notifications")
