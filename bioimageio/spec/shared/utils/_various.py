def is_valid_orcid_id(orcid_id: str):
    """adapted from stdnum.iso7064.mod_11_2.checksum()"""
    check = 0
    for n in orcid_id:
        check = (2 * check + int(10 if n == "X" else n)) % 11
    return check == 1


# def _remove_slash_from_names(data: Dict[str, Any]) -> None:
#     if "name" in data and isinstance(data["name"], str):
#         data["name"] = data["name"].replace("/", "").replace("\\", "")

#     # remove slashes in author/maintainer name
#     authors = data.get("authors")
#     maintainers = data.get("maintainers")
#     persons: list[Any] = (authors if isinstance(authors, list) else []) + (
#         maintainers if isinstance(maintainers, list) else []
#     )
#     for p in persons:
#         if isinstance(p, dict):
#             v = p.get("name")  # type: ignore
#             if isinstance(v, str):
#                 p["name"] = v.replace("/", "").replace("\\", "")
