"""Added servers table

Revision ID: 6b2f1eb1fcf4
Revises: 
Create Date: 2023-06-13 21:52:34.678474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b2f1eb1fcf4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('servers',
    sa.Column('server_id', sa.BigInteger(), nullable=False),
    sa.Column('prefix', sa.String(length=10), nullable=True),
    sa.Column('default_role', sa.BigInteger(), nullable=True),
    sa.Column('welcome_channel', sa.BigInteger(), nullable=True),
    sa.Column('welcome_message', sa.String(length=200), nullable=True),
    sa.Column('leave_channel', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('server_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('servers')
    # ### end Alembic commands ###