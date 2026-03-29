import tiktoken


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count tokens for a given text."""
    enc = tiktoken.get_encoding(model)
    return len(enc.encode(text))


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    model: str = "cl100k_base",
) -> list[dict]:
    """
    Split text into chunks using recursive character splitting.
    Preserves paragraph/sentence boundaries where possible.
    Returns list of {content, chunk_index, token_count}.
    """
    enc = tiktoken.get_encoding(model)

    # Split on paragraph boundaries first
    paragraphs = text.split("\n\n")
    if not paragraphs:
        paragraphs = text.split("\n")

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = len(enc.encode(para))

        # If single paragraph exceeds chunk size, split by sentences
        if para_tokens > chunk_size:
            sentences = _split_sentences(para)
            for sentence in sentences:
                sent_tokens = len(enc.encode(sentence))
                if current_tokens + sent_tokens > chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    # Overlap: keep last portion
                    overlap_text = _get_overlap(current_chunk, chunk_overlap, enc)
                    current_chunk = overlap_text + " " + sentence
                    current_tokens = len(enc.encode(current_chunk))
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
                    current_tokens += sent_tokens
        elif current_tokens + para_tokens > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            overlap_text = _get_overlap(current_chunk, chunk_overlap, enc)
            current_chunk = overlap_text + "\n\n" + para
            current_tokens = len(enc.encode(current_chunk))
        else:
            current_chunk += "\n\n" + para if current_chunk else para
            current_tokens += para_tokens

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return [
        {"content": chunk, "chunk_index": i, "token_count": len(enc.encode(chunk))}
        for i, chunk in enumerate(chunks)
    ]


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def _get_overlap(text: str, overlap_tokens: int, enc) -> str:
    """Get the last N tokens of text as overlap."""
    tokens = enc.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    overlap = enc.decode(tokens[-overlap_tokens:])
    return overlap
