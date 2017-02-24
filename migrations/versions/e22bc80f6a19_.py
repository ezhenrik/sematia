"""empty message

Revision ID: e22bc80f6a19
Revises: 578b96af6329
Create Date: 2017-01-24 12:19:12.870874

"""

# revision identifiers, used by Alembic.
revision = 'e22bc80f6a19'
down_revision = '578b96af6329'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hand', sa.Column('hand_id', sa.String(length=256), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hand', 'hand_id')
    ### end Alembic commands ###
