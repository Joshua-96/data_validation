from typing import List
from data_validation.validation import Function_Mapper, Static_Function_Mapper


def validate_email(value: str) -> None:
    if "@" in value:
        return
    raise ValueError("Invalid Email")



def dynamic_value_fct() -> List[str]:
    return ["gmail.com", "example_uni.edu", "outlook.com"]


Email_Validation = Function_Mapper(func=validate_email, value_kw="value")

allowed_domains = ["gmail.com", "example_uni.edu", "outlook.com"]


def validate_email_precisely(value: str,
                             first_name: str,
                             last_name: str,
                             allowed_domains: List[str]):
    if "@" not in value:
        raise ValueError("Invalid Email, <@> is missing")
    if first_name.lower() not in value.lower():
        raise ValueError(f"first name <{first_name}> missing from email")
    if last_name.lower() not in value.lower():
        raise ValueError(f"first name <{first_name}> missing from email")
    domain = value.split("@")[1]
    enumerated_domains = ",".join(allowed_domains)
    if domain not in allowed_domains:
        raise ValueError(f"domain <{domain}> is missing from domain whitelist <{enumerated_domains}> missing from email")


Precise_Email_Validation = Function_Mapper(
    func=validate_email_precisely,
    value_kw="value",
    # Pass attribute Name to refer to instance field
    first_name="first_name",
    last_name="last_name",
    # Passing static arguments is also possible
    allowed_domains=allowed_domains)

Precise_Email_Validation_dynamic = Function_Mapper(
    func=validate_email_precisely,
    value_kw="value",
    # Pass attribute Name to refer to instance field
    first_name="first_name",
    last_name="last_name",
    # Passing static arguments is also possible
    allowed_domains=Static_Function_Mapper(dynamic_value_fct)
)
