import numpy as np

from app.config import get_settings

BATCH_SIZE = 50
DIMENSIONS = 768


def encode(texts: list[str]) -> np.ndarray:
    from google import genai
    from google.genai import types

    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    config = types.EmbedContentConfig(output_dimensionality=DIMENSIONS)
    vectors = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        reply = client.models.embed_content(model=settings.gemini_embedding_model,
                                            contents=batch, config=config)
        vectors += [item.values for item in reply.embeddings]
    array = np.asarray(vectors, dtype="float32")
    return array / np.linalg.norm(array, axis=1, keepdims=True)  # truncated vectors are not unit length
