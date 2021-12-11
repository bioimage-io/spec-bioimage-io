def is_valid_orcid_id(orcid_id: str):
    """adapted from stdnum.iso7064.mod_11_2.checksum()"""
    check = 0
    for n in orcid_id:
        check = (2 * check + int(10 if n == "X" else n)) % 11
    return check == 1
