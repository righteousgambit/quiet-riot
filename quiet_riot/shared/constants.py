import os

SERVICE_LINKED_ROLES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "service-linked-roles.txt"))
VALID_PRINCIPAL_TYPES = [
    "user",
    "role",
]