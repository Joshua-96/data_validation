from typing import List

from data_validation.function_wrappers import ArgFunctionWrapper, FunctionWrapper

import sample.config as global_vars


def validate_email(value: str) -> None:
    if "@" in value:
        return
    raise ValueError("Invalid Email")


def dynamic_value_fct() -> List[str]:
    # placeholder for an arbitrary data-retrieving logic
    print(global_vars.dbConfig)
    return ["gmail.com", "example_uni.edu", "outlook.com"]


email_Validation = ArgFunctionWrapper(func=validate_email, value_kw="value")
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
        raise ValueError(f"last name <{last_name}> missing from email")
    domain = value.split("@")[1]
    enumerated_domains = ",".join(allowed_domains)
    if domain not in allowed_domains:
        raise ValueError(f"domain <{domain}> is not in domain whitelist: <{enumerated_domains}>")


Precise_Email_Validation = ArgFunctionWrapper(
    func=validate_email_precisely,
    value_kw="value",
    # Pass attribute Name to refer to instance field
    first_name="first_name",
    last_name="last_name",
    # Passing static arguments is also possible
    allowed_domains=allowed_domains)

Precise_Email_Validation_dynamic = ArgFunctionWrapper(
    func=validate_email_precisely,
    value_kw="value",
    # Pass attribute Name to refer to instance field
    first_name="first_name",
    last_name="last_name",
    # Passing static arguments is also possible
    allowed_domains=FunctionWrapper(dynamic_value_fct)
)
