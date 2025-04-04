"""empty message

Revision ID: 758e845a6f61
Revises: 10a7caac41fb
Create Date: 2025-03-03 12:45:06.002839

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '758e845a6f61'
down_revision = '10a7caac41fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(length=200), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('phone')

    # ### end Alembic commands ###
