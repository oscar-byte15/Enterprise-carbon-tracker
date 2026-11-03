from uuid import uuid4


class User:
    def __init__(
        self,
        email: str,
        password_hash: str,
        enterprise_id: str,
        role: str = "admin",
    ):
        self._id = str(uuid4())
        self._email = email.strip().lower()
        self._password_hash = password_hash
        self._enterprise_id = enterprise_id
        self._role = role

    def get_email(self) -> str:
        return self._email

    def set_email(self, email: str) -> None:
        if not email.strip():
            raise ValueError("Email cannot be empty")
        self._email = email.strip().lower()

    def get_role(self) -> str:
        return self._role

    def set_role(self, role: str) -> None:
        if not role.strip():
            raise ValueError("Role cannot be empty")
        self._role = role.strip()


#对应原来 store.py 中的 create_enterprise()、get_enterprise() 
# 和 update_enterprise() 等功能
class Enterprise:
    def __init__(
        self,
        company_name: str,
        industry: str,
        enterprise_id: str | None = None,
    ):
        self._enterprise_id = enterprise_id or str(uuid4())
        self._company_name = ""
        self._industry = ""
        self._address = None

        self.set_company_name(company_name)
        self.set_industry(industry)

    # Getters
    def get_enterprise_id(self) -> str:
        return self._enterprise_id

    def get_company_name(self) -> str:
        return self._company_name

    def get_industry(self) -> str:
        return self._industry

    def get_address(self) -> str | None:
        return self._address

    # Setters
    def set_company_name(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Company name cannot be empty")
        self._company_name = name.strip()

    def set_industry(self, industry: str) -> None:
        if not industry.strip():
            raise ValueError("Industry cannot be empty")
        self._industry = industry.strip()

    def set_address(self, address: str | None) -> None:
        self._address = address.strip() if address else None

    # Configuration method
    def update_profile(
        self,
        company_name: str | None = None,
        industry: str | None = None,
        address: str | None = None,
    ) -> None:
        if company_name is not None:
            self.set_company_name(company_name)
        if industry is not None:
            self.set_industry(industry)
        if address is not None:
            self.set_address(address)


#对应原来项目中create_department()、list_departments() 所管理的部门数据。
class Department:
    def __init__(
        self,
        enterprise_id: str,
        name: str,
        description: str | None = None,
        department_id: str | None = None,
    ):
        self._department_id = department_id or str(uuid4())
        self._enterprise_id = enterprise_id
        self._name = ""
        self._description = None

        self.set_name(name)
        self.set_description(description)

    # Getters
    def get_department_id(self) -> str:
        return self._department_id

    def get_enterprise_id(self) -> str:
        return self._enterprise_id

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str | None:
        return self._description

    # Setters
    def set_name(self, name: str) -> None:
        if not name.strip():
            raise ValueError("Department name cannot be empty")
        self._name = name.strip()

    def set_description(self, description: str | None) -> None:
        self._description = description.strip() if description else None

    # Configuration method
    def update_details(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> None:
        if name is not None:
            self.set_name(name)
        if description is not None:
            self.set_description(description)
