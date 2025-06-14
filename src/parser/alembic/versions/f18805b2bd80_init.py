"""init

Revision ID: f18805b2bd80
Revises:
Create Date: 2025-05-29 11:14:56.517079

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f18805b2bd80"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "auto_parts",
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("article", sa.String(length=128), nullable=False),
        sa.Column("category", sa.String(length=128), nullable=False),
        sa.Column("subcategory", sa.String(length=128), nullable=False),
        sa.Column("product_name", sa.String(length=256), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("type_quantity", sa.String(length=64), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auto_parts")),
        sa.UniqueConstraint(
            "article", "category", "subcategory", name="article_unique_constraint"
        ),
        sa.UniqueConstraint("article", name=op.f("uq_auto_parts_article")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("auto_parts")
    # ### end Alembic commands ###
