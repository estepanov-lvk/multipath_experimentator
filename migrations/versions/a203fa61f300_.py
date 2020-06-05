"""empty message

Revision ID: a203fa61f300
Revises: cbd86bafd14b
Create Date: 2020-02-03 15:16:41.952655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a203fa61f300'
down_revision = 'cbd86bafd14b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('experiment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mode', sa.String(length=10), nullable=True),
    sa.Column('model', sa.String(length=10), nullable=True),
    sa.Column('subflow', sa.Integer(), nullable=True),
    sa.Column('topo', sa.String(length=20), nullable=True),
    sa.Column('poles', sa.Integer(), nullable=True),
    sa.Column('flows', sa.Integer(), nullable=True),
    sa.Column('poles_seed', sa.Integer(), nullable=True),
    sa.Column('routes_seed', sa.Integer(), nullable=True),
    sa.Column('cc', sa.String(length=20), nullable=True),
    sa.Column('distribution', sa.String(length=20), nullable=True),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('probe', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_experiment_cc'), 'experiment', ['cc'], unique=False)
    op.create_index(op.f('ix_experiment_distribution'), 'experiment', ['distribution'], unique=False)
    op.create_index(op.f('ix_experiment_flows'), 'experiment', ['flows'], unique=False)
    op.create_index(op.f('ix_experiment_mode'), 'experiment', ['mode'], unique=False)
    op.create_index(op.f('ix_experiment_model'), 'experiment', ['model'], unique=False)
    op.create_index(op.f('ix_experiment_poles'), 'experiment', ['poles'], unique=False)
    op.create_index(op.f('ix_experiment_poles_seed'), 'experiment', ['poles_seed'], unique=False)
    op.create_index(op.f('ix_experiment_probe'), 'experiment', ['probe'], unique=False)
    op.create_index(op.f('ix_experiment_routes_seed'), 'experiment', ['routes_seed'], unique=False)
    op.create_index(op.f('ix_experiment_subflow'), 'experiment', ['subflow'], unique=False)
    op.create_index(op.f('ix_experiment_time'), 'experiment', ['time'], unique=False)
    op.create_index(op.f('ix_experiment_topo'), 'experiment', ['topo'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_experiment_topo'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_time'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_subflow'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_routes_seed'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_probe'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_poles_seed'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_poles'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_model'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_mode'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_flows'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_distribution'), table_name='experiment')
    op.drop_index(op.f('ix_experiment_cc'), table_name='experiment')
    op.drop_table('experiment')
    # ### end Alembic commands ###
