from app.chunking.text_chunker import chunk_text


def test_short_text_is_single_chunk():
    assert chunk_text("A short clause.") == ["A short clause."]


def test_empty_text_has_no_chunks():
    assert chunk_text("") == []


def test_long_text_is_split_within_chunk_size():
    paragraphs = [f"Clause {i}. " + "The processor shall protect data. " * 10 for i in range(20)]
    text = "\n\n".join(paragraphs)

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 900 for chunk in chunks)
    for i in range(20):
        assert any(f"Clause {i}." in chunk for chunk in chunks)


def test_chunks_overlap_when_splitting_a_single_paragraph():
    text = " ".join(f"word{i}" for i in range(400))

    chunks = chunk_text(text)

    assert len(chunks) > 1
    for previous, current in zip(chunks, chunks[1:]):
        assert current.split()[0] in previous.split()
