class Chunker:
    def split_into_chunks(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[str]:
        """
        Режет text на чанки, с overlap символами перекрытия между соседними чанками.
        """
        chunks = []
        if chunk_size <= 0:
            raise ValueError("Неверная длина")

        if overlap >= chunk_size:
            overlap = chunk_size - 1

        step = chunk_size - overlap
        for i in range(len(text) // step + 1):
            start = i * step
            end = start + chunk_size
            chunk = text[start:end]
            if len(chunk) != 0:
                chunks.append(chunk)
            else:
                pass
        return chunks

    def recursive_split(
        self,
        text: str,
        chunk_size: int = 500,
        separators=None,
    ):
        """
        Рекурсивно режет text на чанки
        """
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]

        if len(separators) == 0:
            return self.split_into_chunks(
                text,
                chunk_size=chunk_size,
                overlap=0,
            )

        sep = separators[0]
        rest_separators = separators[1:]

        pieces = text.split(sep)

        chunks = []
        for piece in pieces:
            if len(piece) <= chunk_size:
                chunks.append(piece)
            else:
                sub_chunks = self.recursive_split(
                    piece,
                    chunk_size=chunk_size,
                    separators=rest_separators
                )
                chunks.extend(sub_chunks)

        return chunks
