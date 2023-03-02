from bioimageio.spec.shared.common import CONSUMER_ID, CONSUMER_VERSION


def report_resource_download(resource_id: str):
    import requests  # not available in pyodide

    uadata = f'&uadata={{"brands":[{{"brand":"{CONSUMER_ID}","version":"{CONSUMER_VERSION or "unknown"}"}}]}}'
    url = f"https://bioimage.matomo.cloud/matomo.php?download=https://doi.org/{resource_id}&idsite=1&rec=1&r=646242&h=13&m=35&s=20&url=http://bioimage.io/#/?id={resource_id}{uadata}"

    r = requests.get(url)
    r.raise_for_status()


if __name__ == "__main__":
    model_doi = "10.5281/zenodo.7614645"
    report_resource_download(model_doi)
    print(
        f"https://bioimage.matomo.cloud/?module=API&method=Actions.getDownload&downloadUrl=https://doi.org/{model_doi}&idSite=1&period=day&date=yesterday&format=JSON&token_auth=anonymous"
    )
