from pony.orm import *


db = Database()


class Device(db.Entity):
    id = PrimaryKey(int, auto=True)
    dc_identify = Required(str, nullable=True)


class FrameData_Linesetup(db.Entity):
    _table_ = 'FrameData'
    id = PrimaryKey(int, auto=True)
    TNDP = Required(int, nullable=True)
    POINTS = Required(str)
    TP = Required(int)


class FrameData_Template(db.Entity):
    id = PrimaryKey(int, auto=True)
    TNDP = Required(int)
    POINTS = Required(str)


class FrameData_OCRData(db.Entity):
    id = PrimaryKey(int, auto=True)
    TNDP = Required(int)
    POINTS = Required(str)


class FrameData_TraceFault(db.Entity):
    id = PrimaryKey(int, auto=True)
    TNDP = Required(int)
    POINTS = Required(unicode)


db.bind("sqlite", "database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)