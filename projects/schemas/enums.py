from enum import Enum


class RoleEnum(str, Enum):
	admin = 'admin'
	normal_user = 'normal_user'
	security = 'security'
	staff = 'staff'

class IntendedUserEnum(str, Enum):
	ONE = 'ONE'
	ALL = 'ALL'
