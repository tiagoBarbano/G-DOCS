"""init

Revision ID: 86e821c8e4d4
Revises: 
Create Date: 2023-06-13 21:16:25.268297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86e821c8e4d4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('area',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome_area', sa.String(), nullable=True),
    sa.Column('token_area', sa.String(), nullable=True),
    sa.Column('caminho_area', sa.String(), nullable=True),
    sa.Column('status_area', sa.Enum('ativo', 'inativo', 'excluido', 'vencido', name='statustypes'), nullable=True),
    sa.Column('data_criacao', sa.DateTime(), nullable=True),
    sa.Column('data_atualizacao', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_area_id'), 'area', ['id'], unique=False)
    op.create_index(op.f('ix_area_nome_area'), 'area', ['nome_area'], unique=False)
    op.create_index(op.f('ix_area_status_area'), 'area', ['status_area'], unique=False)
    op.create_table('documento',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('area_responsavel', sa.String(), nullable=True),
    sa.Column('my_uuid', sa.UUID(), nullable=True),
    sa.Column('nome_documento', sa.String(), nullable=True),
    sa.Column('caminho_documento', sa.String(), nullable=True),
    sa.Column('status_documento', sa.Enum('ativo', 'inativo', 'excluido', 'vencido', name='statustypes'), nullable=True),
    sa.Column('data_criacao', sa.DateTime(), nullable=True),
    sa.Column('data_atualizacao', sa.DateTime(), nullable=True),
    sa.Column('data_inativacao', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documento_area_responsavel'), 'documento', ['area_responsavel'], unique=False)
    op.create_index(op.f('ix_documento_id'), 'documento', ['id'], unique=False)
    op.create_index(op.f('ix_documento_my_uuid'), 'documento', ['my_uuid'], unique=False)
    op.create_index(op.f('ix_documento_nome_documento'), 'documento', ['nome_documento'], unique=False)
    op.create_index(op.f('ix_documento_status_documento'), 'documento', ['status_documento'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_documento_status_documento'), table_name='documento')
    op.drop_index(op.f('ix_documento_nome_documento'), table_name='documento')
    op.drop_index(op.f('ix_documento_my_uuid'), table_name='documento')
    op.drop_index(op.f('ix_documento_id'), table_name='documento')
    op.drop_index(op.f('ix_documento_area_responsavel'), table_name='documento')
    op.drop_table('documento')
    op.drop_index(op.f('ix_area_status_area'), table_name='area')
    op.drop_index(op.f('ix_area_nome_area'), table_name='area')
    op.drop_index(op.f('ix_area_id'), table_name='area')
    op.drop_table('area')
    # ### end Alembic commands ###
