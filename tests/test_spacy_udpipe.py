import tempfile

import pytest
import spacy

from spacy_udpipe import UDPipeModel, download, load

EN = "en"
RO = "ro"
RU = "ru"
SPACY_VERSION = "2.2.4"


@pytest.fixture
def lang() -> str:
    return EN


@pytest.fixture(autouse=True)
def download_lang(lang: str) -> None:
    download(lang=lang)


def test_serialization(lang: str) -> None:
    with tempfile.TemporaryDirectory() as tdir:
        nlp = load(lang=lang)
        nlp.to_disk(tdir)

        udpipe_model = UDPipeModel(lang=lang)
        nlp = spacy.load(tdir, udpipe_model=udpipe_model)


def test_pipe(lang: str) -> None:
    nlp = load(lang=lang)
    assert nlp._meta["lang"] == f"udpipe_{lang}"

    text = "spacy-udpipe still does not support multiprocess execution."
    doc = nlp(text)
    del nlp

    nlp = load(lang=lang)
    texts = [text for _ in range(2)]
    docs = list(nlp.pipe(texts, n_process=-1))

    assert len(docs) == len(texts)
    assert docs[0].to_json() == doc.to_json()
    assert docs[-1].to_json() == doc.to_json()


def test_morph_exception() -> None:
    assert spacy.__version__ <= SPACY_VERSION

    lang = RO
    text = "Ce mai faci?"

    download(lang=lang)

    try:
        nlp = load(lang=lang)
        assert nlp._meta["lang"] == f"udpipe_{lang}"
        doc = nlp(text)
    except ValueError:
        nlp = load(lang=lang, ignore_tag_map=True)
        assert nlp._meta["lang"] == f"udpipe_{lang}"
        doc = nlp(text)

    assert doc


def test_feats() -> None:
    lang = RU
    text = "Я люблю машинное обучение."

    download(lang=lang)

    nlp = load(lang=lang)
    assert nlp._meta["lang"] == f"udpipe_{lang}"
    doc = nlp(text)
    assert doc[2]._.feats == "Case=Acc|Degree=Pos|Gender=Neut|Number=Sing"
