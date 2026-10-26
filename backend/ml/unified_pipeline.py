import os
import sys
import json
import random
import re
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Set
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# Add backend directory to sys.path
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from retrieval.retrieve import retrieve_evidence, load_index

LABEL_VOCABULARY = {"SUPPORT", "CONTRADICT", "NEUTRAL"}

LABEL_MAPPING = {
    # SciFact
    "SUPPORT": "SUPPORT",
    "SUPPORTS": "SUPPORT",
    "CONTRADICT": "CONTRADICT",
    "REFUTE": "CONTRADICT",
    "REFUTES": "CONTRADICT",
    "NEUTRAL": "NEUTRAL",
    "NOT ENOUGH INFO": "NEUTRAL",
    "NOINFO": "NEUTRAL",
    # HealthVer
    "Supports": "SUPPORT",
    "Refutes": "CONTRADICT",
    "Neutral": "NEUTRAL",
    # ManConCorpus
    "ENTAILMENT": "SUPPORT",
    "CONTRADICTION": "CONTRADICT",
    "CONTRADICT": "CONTRADICT",
    "ENTAILE": "SUPPORT",
}

@dataclass
class UnifiedRecord:
    claim_id: str
    claim_text: str
    evidence_id: str
    evidence_text: str
    original_label: str
    normalized_label: str
    source_dataset: str
    source_document_id: str
    provenance: str
    split: str

def normalize_text(text: str) -> str:
    """Carefully normalize whitespace without modifying scientific terms, numbers, or symbols."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def normalize_label(label: str, source: str = "") -> str:
    """Map source label into canonical VeriSci label: SUPPORT, CONTRADICT, NEUTRAL."""
    clean_lbl = str(label).strip()
    if clean_lbl in LABEL_MAPPING:
        return LABEL_MAPPING[clean_lbl]
    clean_upper = clean_lbl.upper()
    if clean_upper in LABEL_MAPPING:
        return LABEL_MAPPING[clean_upper]
    raise ValueError(f"Unsupported label '{label}' encountered from source '{source}'. Expected one of {list(LABEL_MAPPING.keys())}")

class UnifiedDatasetPipeline:
    def __init__(self, data_dir: str = DATA_DIR, processed_dir: str = PROCESSED_DIR, seed: int = 42):
        self.data_dir = data_dir
        self.processed_dir = processed_dir
        self.seed = seed
        os.makedirs(self.processed_dir, exist_ok=True)

    def _load_scifact_corpus(self) -> Dict[str, dict]:
        corpus_path = os.path.join(self.data_dir, "corpus.jsonl")
        if not os.path.exists(corpus_path):
            raise FileNotFoundError(f"SciFact corpus not found at {corpus_path}")
        corpus = {}
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                corpus[str(doc["doc_id"])] = doc
        return corpus

    def load_scifact(self, split: str = "train", include_hard_negatives: bool = True, force_rebuild: bool = False) -> pd.DataFrame:
        """Loads SciFact and maps to unified representation."""
        cache_path = os.path.join(self.processed_dir, f"scifact_{split}.csv")
        if not force_rebuild and os.path.exists(cache_path):
            logging.info(f"Loading cached SciFact {split} from {cache_path}")
            return pd.read_csv(cache_path)

        split_file_map = {
            "train": "claims_train.jsonl",
            "dev": "claims_dev.jsonl",
            "test": "claims_test.jsonl"
        }
        if split not in split_file_map:
            raise ValueError(f"Unknown split '{split}' for SciFact")

        claims_path = os.path.join(self.data_dir, split_file_map[split])
        if not os.path.exists(claims_path):
            raise FileNotFoundError(f"SciFact claims file not found: {claims_path}")

        corpus = self._load_scifact_corpus()
        records: List[UnifiedRecord] = []
        rng = random.Random(self.seed)

        # Set environment variable so live PubMed is bypassed during hard-negative mining
        old_env = os.environ.get("ENABLE_PUBMED")
        os.environ["ENABLE_PUBMED"] = "false"

        try:
            with open(claims_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in tqdm(lines, desc=f"Processing SciFact {split}"):
                data = json.loads(line)
                raw_claim_id = str(data.get("id", ""))
                claim_text = normalize_text(data["claim"])
                evidence = data.get("evidence", {})
                cited_doc_ids = data.get("cited_doc_ids", [])
                gold_sentences = set()

                for doc_id, rationales in evidence.items():
                    doc_id = str(doc_id)
                    if doc_id not in corpus:
                        continue
                    abstract = corpus[doc_id]["abstract"]
                    evidence_sentences = set()

                    for r_idx, rationale in enumerate(rationales):
                        orig_label = rationale["label"]
                        norm_label = normalize_label(orig_label, source="SciFact")
                        for sent_idx in rationale["sentences"]:
                            evidence_sentences.add(sent_idx)
                            gold_sentences.add((doc_id, sent_idx))
                            if sent_idx < len(abstract):
                                ev_text = normalize_text(abstract[sent_idx])
                                records.append(UnifiedRecord(
                                    claim_id=f"scifact_{raw_claim_id}",
                                    claim_text=claim_text,
                                    evidence_id=f"scifact_{doc_id}_{sent_idx}",
                                    evidence_text=ev_text,
                                    original_label=orig_label,
                                    normalized_label=norm_label,
                                    source_dataset="SciFact",
                                    source_document_id=doc_id,
                                    provenance="abstract_rationale",
                                    split=split
                                ))

                    # Same-doc neutral sentences
                    neutral_cands = [i for i in range(len(abstract)) if i not in evidence_sentences]
                    if neutral_cands:
                        sampled = rng.sample(neutral_cands, min(2, len(neutral_cands)))
                        for sent_idx in sampled:
                            records.append(UnifiedRecord(
                                claim_id=f"scifact_{raw_claim_id}",
                                claim_text=claim_text,
                                evidence_id=f"scifact_{doc_id}_{sent_idx}",
                                evidence_text=normalize_text(abstract[sent_idx]),
                                original_label="NEUTRAL",
                                normalized_label="NEUTRAL",
                                source_dataset="SciFact",
                                source_document_id=doc_id,
                                provenance="in_doc_neutral",
                                split=split
                            ))

                # Pure neutral cited documents
                for doc_id in cited_doc_ids:
                    doc_id = str(doc_id)
                    if doc_id not in evidence and doc_id in corpus:
                        abstract = corpus[doc_id]["abstract"]
                        if abstract:
                            sent_idx = rng.randint(0, len(abstract) - 1)
                            records.append(UnifiedRecord(
                                claim_id=f"scifact_{raw_claim_id}",
                                claim_text=claim_text,
                                evidence_id=f"scifact_{doc_id}_{sent_idx}",
                                evidence_text=normalize_text(abstract[sent_idx]),
                                original_label="NEUTRAL",
                                normalized_label="NEUTRAL",
                                source_dataset="SciFact",
                                source_document_id=doc_id,
                                provenance="cited_doc_neutral",
                                split=split
                            ))

                # Hard negative retrieval from SciFact index
                if include_hard_negatives:
                    retrieved = retrieve_evidence(claim_text, top_k=5, doc_threshold=0.01, sent_threshold=0.01)
                    for res in retrieved:
                        if res.get("out_of_scope"):
                            continue
                        doc_id = str(res["doc_id"])
                        sent_idx = res["sentence_idx"]
                        if (doc_id, sent_idx) not in gold_sentences:
                            records.append(UnifiedRecord(
                                claim_id=f"scifact_{raw_claim_id}",
                                claim_text=claim_text,
                                evidence_id=f"scifact_{doc_id}_{sent_idx}",
                                evidence_text=normalize_text(res["evidence_text"]),
                                original_label="NEUTRAL",
                                normalized_label="NEUTRAL",
                                source_dataset="SciFact",
                                source_document_id=doc_id,
                                provenance="hard_negative",
                                split=split
                            ))
        finally:
            if old_env is not None:
                os.environ["ENABLE_PUBMED"] = old_env
            else:
                os.environ.pop("ENABLE_PUBMED", None)

        df = pd.DataFrame([asdict(r) for r in records])
        df = self._clean_and_deduplicate(df, "SciFact", split)
        df.to_csv(cache_path, index=False)
        logging.info(f"Saved processed SciFact {split} ({len(df)} records) to {cache_path}")
        return df

    def load_healthver(self, split: str = "train", force_rebuild: bool = False) -> pd.DataFrame:
        """Loads HealthVer and maps to unified representation."""
        cache_path = os.path.join(self.processed_dir, f"healthver_{split}.csv")
        if not force_rebuild and os.path.exists(cache_path):
            logging.info(f"Loading cached HealthVer {split} from {cache_path}")
            return pd.read_csv(cache_path)

        file_map = {
            "train": "healthver_train.csv",
            "dev": "healthver_dev.csv",
            "test": "healthver_test.csv"
        }
        if split not in file_map:
            raise ValueError(f"Unknown split '{split}' for HealthVer")

        raw_path = os.path.join(self.data_dir, "healthver", file_map[split])
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"HealthVer {split} file not found at {raw_path}")

        raw_df = pd.read_csv(raw_path)
        records: List[UnifiedRecord] = []

        for _, row in raw_df.iterrows():
            claim = normalize_text(str(row["claim"]))
            evidence = normalize_text(str(row["evidence"]))
            orig_lbl = str(row["label"]).strip()
            norm_lbl = normalize_label(orig_lbl, source="HealthVer")
            rec_id = str(row["id"])
            topic_id = str(row.get("topic_ip", ""))

            records.append(UnifiedRecord(
                claim_id=f"healthver_{rec_id}",
                claim_text=claim,
                evidence_id=f"healthver_{rec_id}_ev",
                evidence_text=evidence,
                original_label=orig_lbl,
                normalized_label=norm_lbl,
                source_dataset="HealthVer",
                source_document_id=topic_id,
                provenance=f"healthver_topic_{topic_id}",
                split=split
            ))

        df = pd.DataFrame([asdict(r) for r in records])
        df = self._clean_and_deduplicate(df, "HealthVer", split)
        df.to_csv(cache_path, index=False)
        logging.info(f"Saved processed HealthVer {split} ({len(df)} records) to {cache_path}")
        return df

    def load_mancon(self, split: str = "train", force_rebuild: bool = False) -> pd.DataFrame:
        """Loads ManConCorpus XML and generates sentence pairs partitioned by review ID."""
        cache_path = os.path.join(self.processed_dir, f"mancon_{split}.csv")
        if not force_rebuild and os.path.exists(cache_path):
            logging.info(f"Loading cached ManConCorpus {split} from {cache_path}")
            return pd.read_csv(cache_path)

        xml_path = os.path.join(self.data_dir, "mancon", "corpus.xml")
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"ManConCorpus XML not found at {xml_path}")

        root = ET.parse(xml_path).getroot()
        reviews = root.findall("REVIEW")
        reviews_sorted = sorted(reviews, key=lambda r: str(r.get("REVIEW_PMID", "")))

        # Deterministic 18 / 3 / 3 review split using fixed seed
        rng = random.Random(self.seed)
        review_indices = list(range(len(reviews_sorted)))
        rng.shuffle(review_indices)

        split_indices = {
            "train": set(review_indices[:18]),
            "dev": set(review_indices[18:21]),
            "test": set(review_indices[21:])
        }

        if split not in split_indices:
            raise ValueError(f"Unknown split '{split}' for ManConCorpus")

        selected_reviews = [reviews_sorted[i] for i in split_indices[split]]
        records: List[UnifiedRecord] = []

        # 1. Within-review pairs (Contradiction and Entailment)
        for rev in selected_reviews:
            r_pmid = str(rev.get("REVIEW_PMID", ""))
            claims = rev.findall("CLAIM")
            
            for i in range(len(claims)):
                c1 = claims[i]
                t1 = normalize_text(c1.text or "")
                a1 = c1.get("ASSERTION", "").strip()
                pmid1 = c1.get("PMID", "")
                
                # Also include Question-vs-Claim pair
                q_text = normalize_text(c1.get("QUESTION", ""))
                if q_text and t1:
                    qc_label = "SUPPORT" if a1 == "YS" else "CONTRADICT"
                    records.append(UnifiedRecord(
                        claim_id=f"mancon_q_{r_pmid}_{pmid1}",
                        claim_text=q_text,
                        evidence_id=f"mancon_ev_{pmid1}",
                        evidence_text=t1,
                        original_label=f"QUESTION_{a1}",
                        normalized_label=qc_label,
                        source_dataset="ManConCorpus",
                        source_document_id=pmid1,
                        provenance=f"review_{r_pmid}_question_claim",
                        split=split
                    ))

                for j in range(i + 1, len(claims)):
                    c2 = claims[j]
                    t2 = normalize_text(c2.text or "")
                    a2 = c2.get("ASSERTION", "").strip()
                    pmid2 = c2.get("PMID", "")

                    if not t1 or not t2:
                        continue

                    if a1 == a2:
                        orig_lbl = "ENTAILMENT"
                        norm_lbl = "SUPPORT"
                    else:
                        orig_lbl = "CONTRADICTION"
                        norm_lbl = "CONTRADICT"

                    records.append(UnifiedRecord(
                        claim_id=f"mancon_{r_pmid}_{pmid1}_{pmid2}",
                        claim_text=t1,
                        evidence_id=f"mancon_{r_pmid}_{pmid2}",
                        evidence_text=t2,
                        original_label=orig_lbl,
                        normalized_label=norm_lbl,
                        source_dataset="ManConCorpus",
                        source_document_id=f"{pmid1}_{pmid2}",
                        provenance=f"review_{r_pmid}_within_review",
                        split=split
                    ))

        # 2. Across-review pairs (Neutral) strictly within the split's reviews
        all_split_claims = []
        for rev in selected_reviews:
            r_pmid = str(rev.get("REVIEW_PMID", ""))
            for c in rev.findall("CLAIM"):
                txt = normalize_text(c.text or "")
                if txt:
                    all_split_claims.append((r_pmid, c.get("PMID", ""), txt))

        cross_pairs = []
        for i in range(len(all_split_claims)):
            for j in range(i + 1, len(all_split_claims)):
                r1, p1, t1 = all_split_claims[i]
                r2, p2, t2 = all_split_claims[j]
                if r1 != r2:
                    cross_pairs.append((r1, p1, t1, r2, p2, t2))

        # Sample neutral pairs to balance dataset
        num_entail_contra = len(records)
        target_neutrals = min(num_entail_contra, len(cross_pairs))
        sampled_neutrals = rng.sample(cross_pairs, target_neutrals)

        for r1, p1, t1, r2, p2, t2 in sampled_neutrals:
            records.append(UnifiedRecord(
                claim_id=f"mancon_neutral_{r1}_{r2}_{p1}_{p2}",
                claim_text=t1,
                evidence_id=f"mancon_ev_{p2}",
                evidence_text=t2,
                original_label="NEUTRAL",
                normalized_label="NEUTRAL",
                source_dataset="ManConCorpus",
                source_document_id=f"{p1}_{p2}",
                provenance=f"cross_review_{r1}_{r2}",
                split=split
            ))

        df = pd.DataFrame([asdict(r) for r in records])
        df = self._clean_and_deduplicate(df, "ManConCorpus", split)
        df.to_csv(cache_path, index=False)
        logging.info(f"Saved processed ManConCorpus {split} ({len(df)} records) to {cache_path}")
        return df

    def _clean_and_deduplicate(self, df: pd.DataFrame, dataset_name: str, split: str) -> pd.DataFrame:
        """Validates fields, removes exact duplicates, and reports counts."""
        initial_count = len(df)
        # Drop null or empty texts
        df = df[df["claim_text"].str.strip().str.len() > 0]
        df = df[df["evidence_text"].str.strip().str.len() > 0]
        # Drop duplicates on (claim_text, evidence_text)
        df = df.drop_duplicates(subset=["claim_text", "evidence_text"])
        final_count = len(df)
        dropped = initial_count - final_count
        if dropped > 0:
            logging.info(f"[{dataset_name} {split}] Excluded {dropped} duplicate/empty records. Remaining: {final_count}")
        return df

    def get_unified_dataset(self, splits: List[str] = ["train"], datasets: List[str] = ["scifact", "healthver", "mancon"], force_rebuild: bool = False) -> pd.DataFrame:
        """Combines requested datasets and splits into a single unified DataFrame with leakage verification."""
        dfs = []
        for ds in datasets:
            ds_lower = ds.lower().strip()
            for sp in splits:
                if ds_lower == "scifact":
                    df = self.load_scifact(split=sp, force_rebuild=force_rebuild)
                elif ds_lower == "healthver":
                    df = self.load_healthver(split=sp, force_rebuild=force_rebuild)
                elif ds_lower in ["mancon", "manconcorpus"]:
                    df = self.load_mancon(split=sp, force_rebuild=force_rebuild)
                else:
                    raise ValueError(f"Unknown dataset '{ds}'")
                dfs.append(df)

        combined = pd.concat(dfs, ignore_index=True)
        # Deduplicate across combined dataset
        before = len(combined)
        combined = combined.drop_duplicates(subset=["claim_text", "evidence_text"])
        after = len(combined)
        if before - after > 0:
            logging.info(f"Removed {before - after} cross-dataset duplicate pairs. Final combined size: {after}")

        return combined

    def verify_leakage(self, train_df: pd.DataFrame, eval_df: pd.DataFrame) -> Tuple[int, int]:
        """Checks if any exact (claim, evidence) pair appears in both train and eval."""
        train_pairs = set(zip(train_df["claim_text"], train_df["evidence_text"]))
        eval_pairs = set(zip(eval_df["claim_text"], eval_df["evidence_text"]))
        exact_overlap = train_pairs.intersection(eval_pairs)

        train_claims = set(train_df["claim_text"])
        eval_claims = set(eval_df["claim_text"])
        claim_overlap = train_claims.intersection(eval_claims)

        logging.info(f"Leakage Check: Exact Pair Overlap = {len(exact_overlap)}, Claim Text Overlap = {len(claim_overlap)}")
        return len(exact_overlap), len(claim_overlap)
