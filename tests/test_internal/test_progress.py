from bioimageio.spec._internal.progress import Progressbar


def _test_progress_impl(pbar: Progressbar):
    pbar.total = 10
    pbar.set_description("round 1")
    for _ in range(3):
        pbar.update(2)

    pbar.reset()
    pbar.set_description("round 2")
    pbar.total = 2
    for _ in range(2):
        pbar.update(1)

    pbar.close()


def test_progress_tqdm():
    from tqdm import tqdm

    _test_progress_impl(tqdm())


def test_progress_rich():
    from bioimageio.spec._internal.progress import RichOverallProgress

    pbar_class = RichOverallProgress()
    pbar = pbar_class()
    _test_progress_impl(pbar)
