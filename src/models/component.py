import enum

from sqlalchemy import Column, Integer, String, Enum, Table, ForeignKey, or_, select, cast, union_all
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped

Base = declarative_base()


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    component_nomn = Column(String)
    component_gent = Column(String)
    component_datv = Column(String)
    component_accs = Column(String)
    component_ablt = Column(String)
    component_loct = Column(String)
    gender = Column(String)
    popularity = Column(Integer)
    components = None


class Relation(Base):
    __tablename__ = "relations"

    component_id_1 = Column(Integer, ForeignKey('components.id'), primary_key=True)
    component_id_2 = Column(Integer, ForeignKey('components.id'), primary_key=True)


related = union_all(
    select(Relation.component_id_1.label('from_comp'), Relation.component_id_2.label('to_comp')),
    select(Relation.component_id_2.label('from_comp'), Relation.component_id_1.label('to_comp'))
).alias("related")

Component.components = relationship(
    "Component",
    secondary=related,
    primaryjoin=Component.id == related.c.from_comp,
    secondaryjoin=Component.id == related.c.to_comp,
    lazy='dynamic'
)
