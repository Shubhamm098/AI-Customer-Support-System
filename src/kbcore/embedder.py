"""Optional local embeddings. Returns None if the model isn't available."""
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None
_tried = False


def _get_model():
    global _model, _tried
    if _tried:
        return _model
    _tried = True
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    except Exception as e:  # missing package, no network, etc.
        print(f"[kbcore] embeddings unavailable, keyword-only mode ({e.__class__.__name__})")
        _model = None
    return _model


def embed(texts: list[str]) -> np.ndarray | None:
    model = _get_model()
    if model is None:
        return None
    return np.asarray(model.encode(texts, normalize_embeddings=True), dtype=np.float32)