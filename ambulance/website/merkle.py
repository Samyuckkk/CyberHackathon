import hashlib, json
from typing import List, Tuple

def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical_json(obj) -> bytes:
    """Convert dict -> stable JSON bytes for hashing (sorts keys & removes spaces)."""
    return json.dumps(obj, separators=(',', ':'), sort_keys=True).encode()

def leaf_hash(sample: dict) -> str:
    """Hash a single vitals reading into a leaf."""
    return _sha256(canonical_json(sample))

def pair_hash(left: str, right: str) -> str:
    """Hash two hex digests together."""
    return _sha256(bytes.fromhex(left) + bytes.fromhex(right))

def merkle_root_from_leaves(leaves: List[str]) -> str:
    """Compute Merkle root from list of leaf hashes."""
    if not leaves:
        return _sha256(b"")
    current = leaves[:]
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else current[i]
            next_level.append(pair_hash(left, right))
        current = next_level
    return current[0]

def merkle_root_from_samples(samples: List[dict]) -> str:
    """Compute root directly from list of vitals samples (dicts)."""
    leaves = [leaf_hash(s) for s in samples]
    return merkle_root_from_leaves(leaves)
