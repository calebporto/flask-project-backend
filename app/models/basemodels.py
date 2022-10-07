from datetime import date
from typing import Optional
from pydantic import BaseModel

class Send_User(BaseModel):
    name: str
    email: str
    hash: str
    cep: str
    address: str
    gender: str
    tel: str
    birth: date

class Simple_User(BaseModel):
    id: int
    name: str

class Get_User(BaseModel):
    id: int = -1
    email: str = ''

class User_Loader(BaseModel):
    id: Optional[int]
    name: str
    email: str
    hash: str
    is_admin: bool
    is_treasurer: bool
    is_secretary: bool
    is_adviser: bool
    is_designer: bool

class UserAdd(BaseModel):
    user_to_del: Optional[int]
    name: str
    email: str
    hash: str
    is_admin: bool = False
    is_designer: bool = False

class User_Data(BaseModel):
    cep: str
    address: str
    gender: str
    tel: str
    birth: date
    added: Optional[date]

class User_With_Data(BaseModel):
    id: int = -1
    name: str = '--'
    email: str = '--'
    hash: Optional[str]
    cep: str = '--'
    address: str = '--'
    gender: str = '--'
    tel: str = '--'
    birth: date = 0000-0-0
    added: Optional[date] = 0000-0-0

class User_Update(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[str]
    hash: Optional[str]
    is_admin: Optional[bool]
    is_designer: Optional[bool]
    cep: Optional[str]
    address: Optional[str]
    gender: Optional[str]
    tel: Optional[str]
    birth: Optional[date]
    added: Optional[date]

class Tithe_List(BaseModel):
    value: float = 0
    tithe_date: date = 0000-0-0
    treasurer: str = '--'

class Add_User(BaseModel):
    user: UserAdd
    user_data: User_Data

class Tithe(BaseModel):
    user_id: int
    value: float
    tithe_date: date
    treasurer_id: int

class History_Tithe(BaseModel):
    tithe_date: str
    name: str
    value: str

class Offer(BaseModel):
    value: float
    offer_date: date
    treasurer_id: int

class History_Offer(BaseModel):
    value: str
    offer_date: str
    treasurer_id: int

class Expense(BaseModel):
    value: float
    description: str
    expense_date: date
    treasurer_id: int

class History_Expense(BaseModel):
    value: str
    description: str
    expense_date: str

class History_Finance(BaseModel):
    ref: str
    entry: str
    issues: str
    period_balance: str
    total_balance: str

class Permission(BaseModel):
    id: Optional[int]
    name: Optional[str]
    permission1: Optional[bool]
    permission2: Optional[bool]
    permission3: Optional[bool]
    permission4: Optional[bool]
    permission5: Optional[bool]
    permission6: Optional[bool]
    permission7: Optional[bool]
    permission8: Optional[bool]
    permission9: Optional[bool]
    permission10: Optional[bool]