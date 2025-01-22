def test_set_github_warning():
    from bioimageio.spec._internal.gh_utils import set_github_warning

    set_github_warning("Warning on GH", message="This is a test warning")
