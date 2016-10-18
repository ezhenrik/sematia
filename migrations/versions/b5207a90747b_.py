"""empty message

Revision ID: b5207a90747b
Revises: 62a3369dcfa5
Create Date: 2016-10-12 12:26:35.134471

"""

# revision identifiers, used by Alembic.
revision = 'b5207a90747b'
down_revision = '62a3369dcfa5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('layertreebank', sa.Column('arethusa_id', sa.Integer(), nullable=True))
    op.add_column('layertreebank', sa.Column('arethusa_publication_id', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('layertreebank', 'arethusa_publication_id')
    op.drop_column('layertreebank', 'arethusa_id')
    ### end Alembic commands ###
