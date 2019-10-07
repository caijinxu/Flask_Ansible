from app.models.base import Base, db
from sqlalchemy import Column, String, Text, SmallInteger, Integer, ForeignKey


class PlayBook(Base):
    __tablename__ = "playbook"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, unique=True, comment='playbook名')
    remark = Column(Text, nullable=False, comment='备注')
    content = Column(Text, nullable=False, comment='yaml文件内容')

