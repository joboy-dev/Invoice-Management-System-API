"""add_payments_table_columns

Revision ID: 73716f2ab439
Revises: 3b1de5ccc43b
Create Date: 2024-05-22 10:42:13.142471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73716f2ab439'
down_revision: Union[str, None] = '3b1de5ccc43b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('payments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('amount_paid', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False),
    sa.Column('payment_date', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('invoice_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    # ### end Alembic commands ###
