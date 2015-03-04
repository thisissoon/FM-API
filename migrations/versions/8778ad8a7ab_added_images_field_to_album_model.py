"""Added images field to Album model

Revision ID: 8778ad8a7ab
Revises: 2937e25e93cd
Create Date: 2015-03-03 18:01:29.738011

"""

# revision identifiers, used by Alembic.
revision = '8778ad8a7ab'
down_revision = '2937e25e93cd'

from alembic import op  # noqa
import sqlalchemy as sa  # noqa
import fm  # noqa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('album', sa.Column('images', postgresql.JSON(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('album', 'images')
    ### end Alembic commands ###