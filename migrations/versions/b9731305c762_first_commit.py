"""first commit

Revision ID: b9731305c762
Revises: 
Create Date: 2020-06-13 16:39:25.854118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9731305c762'
down_revision = None
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
    op.create_table('server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('servername', sa.String(length=20), nullable=True),
    sa.Column('server_ip', sa.String(length=15), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_server_server_ip'), 'server', ['server_ip'], unique=True)
    op.create_index(op.f('ix_server_servername'), 'server', ['servername'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('VM',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vm_name', sa.String(length=20), nullable=True),
    sa.Column('vm_control_ip', sa.String(length=15), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_VM_vm_control_ip'), 'VM', ['vm_control_ip'], unique=True)
    op.create_index(op.f('ix_VM_vm_name'), 'VM', ['vm_name'], unique=True)
    op.create_table('server_interface',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('interface_name', sa.String(length=20), nullable=True),
    sa.Column('server_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['server_id'], ['server.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_server_interface_interface_name'), 'server_interface', ['interface_name'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_server_interface_interface_name'), table_name='server_interface')
    op.drop_table('server_interface')
    op.drop_index(op.f('ix_VM_vm_name'), table_name='VM')
    op.drop_index(op.f('ix_VM_vm_control_ip'), table_name='VM')
    op.drop_table('VM')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_server_servername'), table_name='server')
    op.drop_index(op.f('ix_server_server_ip'), table_name='server')
    op.drop_table('server')
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
