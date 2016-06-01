"""empty message

Revision ID: 6c80bc3e5c3f
Revises: 5a2d577011a4
Create Date: 2016-02-11 16:39:31.356684

"""

# revision identifiers, used by Alembic.
revision = '6c80bc3e5c3f'
down_revision = '5a2d577011a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hand', sa.Column('meta_addressee_title', sa.UnicodeText(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hand', 'meta_addressee_title')
    ### end Alembic commands ###
