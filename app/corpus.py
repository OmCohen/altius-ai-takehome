"""Corpus loader and simple chunking utilities.

This module provides a small, production-ready helper for loading a corpus
of markdown summaries and converting them into searchable chunks. It is
intended to be small, dependency-light, and easy for cross-team use.

Key responsibilities:
- Read `metadata.csv` to enrich summaries (if present).
- Load markdown summary files from `Quarterly Report Summaries/`.
- Split documents into sections using heading markers (## - ######).
- Produce `Document` and `Chunk` records consumed by the retriever.

Operational notes for teams:
- Files are expected under `DATA_DIR/Quarterly Report Summaries/` and the
  metadata file `DATA_DIR/metadata.csv` (optional).
- Date parsing is lenient: we try `DD/MM/YYYY` for metadata dates and
  ISO `YYYY-MM-DD` for period labeling, but fall back to original values
  when parsing fails. Tests should include malformed and missing dates.
- The loader is stateless and safe to call at startup; it returns plain
  dataclasses so other components can index them (e.g., TF-IDF or
  embeddings). For large corpora consider streaming or incremental
  indexing instead of loading all chunks into memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

import pandas as pd


SECTION_PATTERN = re.compile(r"^#{2,6}\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Document:
    """A high-level representation of a single summary file.

    Attributes
    - document_id: filename stem used as unique id
    - summary_file: source markdown filename (keeps display names clear)
    - source_file: original source (pdf) filename where available
    - deal_name: business identifier for the deal (from metadata)
    - date: normalized date string where possible
    - reporting_period: human-friendly period label (e.g. 'Q1 2022')
    - text: full markdown content of the summary
    """
    document_id: str
    summary_file: str
    source_file: str
    deal_name: str
    date: str
    reporting_period: str
    text: str


@dataclass(frozen=True)
class Chunk:
    """A searchable chunk derived from a `Document`.

    Chunks are intentionally small, self-contained passages intended for
    vectorization or TF-IDF indexing. `searchable_text` concatenates a
    few metadata fields with body text to help keyword matches include
    contextual signals like the reporting period or deal name.
    """
    document_id: str
    summary_file: str
    source_file: str
    deal_name: str
    date: str
    reporting_period: str
    section: str
    text: str
    searchable_text: str


@dataclass
class Corpus:
    """Simple container for the loaded corpus.

    - `documents` is the full-document metadata and text list
    - `chunks` is the flattened list of `Chunk` objects for indexing
    """
    documents: list[Document]
    chunks: list[Chunk]


class CorpusLoader:
    """Load summaries and metadata, producing `Corpus` objects.

    Usage
    -----
    loader = CorpusLoader(Path("data"))
    corpus = loader.load()

    The loader reads `metadata.csv` if present to enrich filenames and
    deal-level attributes. It will not raise for missing metadata; instead
    it returns best-effort values so callers can decide how to handle
    missing context.
    """

    def __init__(self, data_dir: Path):
        """Initialize with the repository `data` directory.

        Parameters
        - data_dir: Path to the directory containing `metadata.csv` and the
          `Quarterly Report Summaries/` folder.
        """
        self.data_dir = data_dir

    def load(self) -> Corpus:
        """Load metadata and all markdown summaries and produce a `Corpus`.

        The method is designed to be called at process startup. It returns
        the full set of `Document` and `Chunk` objects; callers should
        index `chunks` immediately (e.g., build TF-IDF matrix) and then
        discard the loader if memory is a concern.
        """
        metadata = self._load_metadata()
        documents: list[Document] = []
        chunks: list[Chunk] = []
        summaries_dir = self.data_dir / "Quarterly Report Summaries"
        for path in sorted(summaries_dir.glob("*.md")):
            # Read with fallbacks: ignore encoding errors to avoid crash on
            # malformed files; unit tests should assert file encodings.
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            row = metadata.get(path.name, {})
            # Prefer explicit file name from metadata, otherwise infer pdf name
            source_file = str(row.get("File Name", path.name.replace("_summary_public.md", ".pdf")))
            deal_name = str(row.get("Deal Name", ""))
            date = self._normalize_date(str(row.get("Date", "")))
            reporting_period = self._period_label(date)
            document_id = path.stem
            documents.append(
                Document(
                    document_id=document_id,
                    summary_file=path.name,
                    source_file=source_file,
                    deal_name=deal_name,
                    date=date,
                    reporting_period=reporting_period,
                    text=text,
                )
            )
            # Convert the document into searchable, indexable chunks
            chunks.extend(self._chunk_document(document_id, path.name, source_file, deal_name, date, reporting_period, text))
        return Corpus(documents=documents, chunks=chunks)

    def _load_metadata(self) -> dict[str, dict]:
        """Read `metadata.csv` and return a mapping of summary filename -> row dict.

        The function tolerates missing files and non-standard column names for
        the summary filename. Only rows with a non-empty summary filename are
        returned in the mapping.
        """
        meta_path = self.data_dir / "metadata.csv"
        if not meta_path.exists():
            return {}
        frame = pd.read_csv(meta_path)
        mapping: dict[str, dict] = {}
        for _, row in frame.iterrows():
            # Support multiple metadata column name conventions
            summary_file = row.get("Summary File") or row.get("Summary_File")
            if isinstance(summary_file, str) and summary_file.strip():
                mapping[summary_file.strip()] = row.to_dict()
        return mapping

    def _chunk_document(
        self,
        document_id: str,
        summary_file: str,
        source_file: str,
        deal_name: str,
        date: str,
        reporting_period: str,
        text: str,
    ) -> list[Chunk]:
        """Split a document into sections and return `Chunk` objects.

        Behavior notes:
        - If the markdown contains heading matches (## - ######) we split
          into those sections and include a leading Overview if present.
        - We always include a final "Full summary" chunk to make it easy to
          cite the whole document even when sectioned. We avoid creating
          duplicate "Full summary" chunks.
        """
        sections = self._split_sections(text)
        chunks: list[Chunk] = []
        for section, body in sections:
            cleaned = body.strip()
            if not cleaned:
                continue
            # `searchable_text` intentionally includes the section title,
            # reporting_period and deal/source metadata to increase the
            # chance of keyword matches matching context fields.
            chunks.append(
                Chunk(
                    document_id=document_id,
                    summary_file=summary_file,
                    source_file=source_file,
                    deal_name=deal_name,
                    date=date,
                    reporting_period=reporting_period,
                    section=section,
                    text=cleaned,
                    searchable_text=" ".join([section, reporting_period, source_file, deal_name, cleaned]),
                )
            )
        # Ensure a fallback full-document chunk exists. This is useful so the
        # retriever can cite the whole summary even if a query doesn't match
        # a specific section. Avoid duplicates of the "Full summary" chunk.
        if not chunks:
            chunks.append(
                Chunk(
                    document_id=document_id,
                    summary_file=summary_file,
                    source_file=source_file,
                    deal_name=deal_name,
                    date=date,
                    reporting_period=reporting_period,
                    section="Full summary",
                    text=text,
                    searchable_text=" ".join([reporting_period, source_file, deal_name, text]),
                )
            )
        elif all(chunk.section != "Full summary" for chunk in chunks):
            chunks.append(
                Chunk(
                    document_id=document_id,
                    summary_file=summary_file,
                    source_file=source_file,
                    deal_name=deal_name,
                    date=date,
                    reporting_period=reporting_period,
                    section="Full summary",
                    text=text,
                    searchable_text=" ".join([reporting_period, source_file, deal_name, text]),
                )
            )
        return chunks

    def _split_sections(self, text: str) -> list[tuple[str, str]]:
        """Return `(section_title, body)` pairs found in the markdown `text`.

        - If no heading matches are found we return a single `('Full summary', text)`.
        - Leading content before the first heading is labeled as `Overview`.
        """
        matches = list(SECTION_PATTERN.finditer(text))
        if not matches:
            return [("Full summary", text)]
        sections: list[tuple[str, str]] = []
        lead = text[: matches[0].start()].strip()
        if lead:
            sections.append(("Overview", lead))
        for index, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections.append((title, body))
        return sections

    def _normalize_date(self, value: str) -> str:
        """Try to parse common date formats and return ISO date string.

        We accept `DD/MM/YYYY` from the metadata and fall back to the
        original `value` on failure (so missing or weird values are preserved).
        """
        try:
            return datetime.strptime(value, "%d/%m/%Y").date().isoformat()
        except Exception:
            return value

    def _period_label(self, value: str) -> str:
        """Convert an ISO `YYYY-MM-DD` date string to a quarter label like `Q1 2022`.

        Returns the original `value` or `Unknown period` if parsing fails.
        """
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return value or "Unknown period"
        quarter = (parsed.month - 1) // 3 + 1
        return f"Q{quarter} {parsed.year}"