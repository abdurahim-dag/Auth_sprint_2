"""partitions for accounting

Revision ID: 27dc0a022f95
Revises: 4a589083212b
Create Date: 2023-06-04 11:09:33.264021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27dc0a022f95'
down_revision = '4a589083212b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            create table if not exists accounting_p
            (
                id      serial,
                user_id integer                                not null,
                type    varchar(30)                            not null,
                ts      timestamp with time zone default now() not null,
                params  varchar                                not null
            ) partition by range (ts);
            
            CREATE TABLE accounting_before_y2023m6 PARTITION OF accounting_p
                FOR VALUES FROM ('2000-01-01') TO ('2023-06-01');
            
            CREATE TABLE measurement_y2023m06 PARTITION OF accounting_p
                FOR VALUES FROM ('2023-06-01') TO ('2023-07-01');

            CREATE TABLE measurement_y2023m07 PARTITION OF accounting_p
                FOR VALUES FROM ('2023-07-01') TO ('2023-08-01');

            CREATE TABLE measurement_y2023m08 PARTITION OF accounting_p
                FOR VALUES FROM ('2023-08-01') TO ('2023-09-01');
            
            insert into accounting_p
            select * from accounting;
            
            drop table accounting;
            
            alter table accounting_p rename to accounting;        
        """
    )


def downgrade() -> None:
    op.execute(
        """
            create table if not exists accounting_
            (
                id      serial,
                user_id integer                                not null,
                type    varchar(30)                            not null,
                ts      timestamp with time zone default now() not null,
                params  varchar                                not null
            );
           
            insert into accounting_
            select * from accounting;
            
            drop table accounting;
            
            alter table accounting_ rename to accounting;        
        """
    )

