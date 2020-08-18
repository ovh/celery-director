import base64
import hashlib
from pathlib import Path
from urllib.request import urlretrieve

import click

from director.context import pass_ctx

DEPENDENCIES = [
    (
        "https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.min.js",
        "sha256-ngFW3UnAN0Tnm76mDuu7uUtYEcG3G5H1+zioJw3t+68=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/vue-router@3.3.4/dist/vue-router.min.js",
        "sha256-87g98o5+aw7/ExJ9tBjvH8zz46FJ7hiylPtNFcPvsSw=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/vuex@3.1.2/dist/vuex.min.js",
        "sha256-LfE9mPMjeOg3dTn1sESY2Xvdbq7gAhONtkxacnr7FSA=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/vuetify@2.3.8/dist/vuetify.min.js",
        "sha256-b4RV6u+xflpPubfyN5gdooQRpDjROUcaCCSWbKQNX9Y=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/moment@2.24.0/min/moment.min.js",
        "sha256-4iQZ6BVL4qNKlQ27TExEhBN1HFPvAvAMbFavKKosSWQ=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/axios@0.19.0/dist/axios.min.js",
        "sha256-S1J4GVHHDMiirir9qsXWc8ZWw74PHHafpsHp5PXtjTs=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/d3@5.16.0/dist/d3.min.js",
        "sha256-Xb6SSzhH3wEPC4Vy3W70Lqh9Y3Du/3KxPqI2JHQSpTw=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/dagre-d3@0.6.4/dist/dagre-d3.min.js",
        "sha256-dPm4TA8Y9PY5q5mmtWMkRGOCMHJDKy34ZrxdbBGA9cs=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/vuetify@2.3.8/dist/vuetify.min.css",
        "sha256-aS2abSwj+AMqtAmTglCnsg9GkAyDUKSCFd4xNdLX/AA=",
        None,
    ),
    (
        "https://cdn.jsdelivr.net/npm/@mdi/font@5.5.55/css/materialdesignicons.min.css",
        "sha256-HCkcFMiRi/WMAXrgcUj/C5aoUrPtvHxpfbOIlwdsNtg=",
        "mdi",
    ),
    (
        "https://fonts.gstatic.com/s/roboto/v20/KFOkCnqEu92Fr1MmgVxFIzIXKMnyrYk.woff2",
        "sha256-zlHOyHhuN60+uGhmzvAy+DRFPdAFH1q7iQet5ST8m1E=",
        "fonts",
    ),
    (
        "https://cdn.jsdelivr.net/npm/@mdi/font@4.7.95/fonts/materialdesignicons-webfont.woff2",
        "sha256-Q2IIvBQJrnRI6+hNPamcSie+O6BJ7exgMv6P3r3ZzIc=",
        "fonts",
    ),
]


def compute_sri_hash(filename, block_size=4096):
    """
    Compute a SRI-compliant hash with SHA256
    :param filename: path to the file
    :param block_size: size of the block for reading binary data
    :return: a base64-encoded hash
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256_hash.update(block)
        b64_encoded_str = base64.b64encode(sha256_hash.digest())
        return b64_encoded_str.decode()


@click.command()
@pass_ctx
def dlassets(ctx):
    """Download the required static assets"""
    static_path = Path(ctx.app.config["STATIC_FOLDER"])

    if static_path == Path(ctx.app.config["DIRECTOR_HOME"]) / "static":
        Path(static_path).mkdir(parents=True, exist_ok=True)

    for (dep_url, dep_hash, dep_custom_path) in DEPENDENCIES:
        # Get the name of the output file
        _, dep_filename = dep_url.rsplit("/", 1)

        if not dep_custom_path:
            path = static_path / dep_filename
        else:
            path = static_path / dep_custom_path / dep_filename
            Path(static_path / dep_custom_path).mkdir(parents=True, exist_ok=True)

        click.echo(f"Downloading {dep_filename} in {path}")

        # Download the file from the CDN
        try:
            urlretrieve(dep_url, str(path))
        except Exception as err:
            click.echo(click.style(f"The command encountered an error {err}", fg="red"))
            raise click.Abort()

        # Remove the "shaXXX-" part
        _, hash_value = dep_hash.split("-", 1)

        assert compute_sri_hash(str(path)) == hash_value
