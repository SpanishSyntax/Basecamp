"""Resolution logic for roles, document targets, and aliases."""

from flaker.core.models import Role


def resolve_role_target(
    role_key: str, target_input: str, roles_db: dict[str, Role]
) -> str | None:
    """Resolves target_input against role's target definitions or returns None."""
    if role_key not in roles_db:
        return None
    role = roles_db[role_key]
    if not role.targets:
        return None
    t_clean = target_input.strip().lower()
    for canonical_name, meta in role.targets.items():
        if t_clean == canonical_name.lower():
            return canonical_name
        aliases = [a.lower() for a in meta.get("aliases", [])]
        if t_clean in aliases:
            return canonical_name
    return None


def find_role_for_standalone_target(
    target_input: str, roles_db: dict[str, Role]
) -> tuple[str, str] | None:
    """
    Checks if target_input is a valid target for any role with targets.
    Returns (role_key, canonical_target_name) or None.
    """
    for role_key, role in roles_db.items():
        if role.targets:
            canonical = resolve_role_target(role_key, target_input, roles_db)
            if canonical:
                return role_key, canonical
    return None
