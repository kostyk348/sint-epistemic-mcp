from __future__ import annotations

from fastmcp import FastMCP

from config import NAME, VERSION
from epistemic.calibration import CalibrationStore
from epistemic.status import EpistemicStatus
from epistemic.store import ClaimStore

server = FastMCP(NAME, version=VERSION)
claim_store = ClaimStore()
cal_store = CalibrationStore()


@server.tool()
def epistemic_register(
    claim: str,
    status: str,
    confidence: float,
    source: str = "agent",
    domain: str = "general",
) -> dict:
    if not EpistemicStatus.validate(status):
        return {"error": f"Invalid status. Must be one of {EpistemicStatus.valid()}"}
    if not (0.0 <= confidence <= 1.0):
        return {"error": "confidence must be between 0.0 and 1.0"}
    c = claim_store.add(claim, status, confidence, source, domain)
    return {"id": c.id, "claim": c.claim, "status": c.status, "confidence": c.confidence,
            "source": c.source, "domain": c.domain, "timestamp": c.timestamp}


@server.tool()
def epistemic_status(claim_query: str = "", domain: str = "") -> list[dict]:
    results = claim_store.search(query=claim_query, domain=domain)
    return [c.to_dict() for c in results]


@server.tool()
def epistemic_calibrate(domain: str) -> dict:
    cal = cal_store.get_calibration(domain)
    if cal is None:
        return {"domain": domain, "predictions_count": 0, "correct_count": 0,
                "accuracy": 0.0, "message": "No calibration data for this domain"}
    return {"domain": cal.domain, "predictions_count": cal.predictions_count,
            "correct_count": cal.correct_count, "accuracy": round(cal.accuracy, 4)}


@server.tool()
def epistemic_gaps(domain: str = "") -> list[dict]:
    all_domains = [domain] if domain else list(claim_store.domains())
    gaps = []
    for d in all_domains:
        claims = claim_store.by_domain(d)
        total = len(claims)
        if total == 0:
            continue
        verified = sum(1 for c in claims if c.status == "VERIFIED")
        assumed = sum(1 for c in claims if c.status == "ASSUMED")
        uncertain = sum(1 for c in claims if c.status == "UNCERTAIN")
        inferred = sum(1 for c in claims if c.status == "INFERRED")
        gap_ratio = (assumed + uncertain) / total if total > 0 else 0.0
        gaps.append({
            "domain": d,
            "total_claims": total,
            "verified": verified,
            "inferred": inferred,
            "assumed": assumed,
            "uncertain": uncertain,
            "gap_ratio": round(gap_ratio, 4),
        })
    return sorted(gaps, key=lambda g: g["gap_ratio"], reverse=True)


@server.tool()
def epistemic_graph(domain: str = "") -> dict:
    claims = claim_store.by_domain(domain) if domain else claim_store.all()
    nodes = []
    edges = []
    for c in claims:
        nodes.append({
            "id": c.id,
            "label": c.claim[:60],
            "status": c.status,
            "confidence": c.confidence,
            "domain": c.domain,
        })
    for i, a in enumerate(claims):
        for b in claims[i + 1:]:
            if a.domain == b.domain:
                edges.append({
                    "source": a.id,
                    "target": b.id,
                    "relation": "same_domain",
                    "domain": a.domain,
                })
    return {"nodes": nodes, "edges": edges, "count": len(nodes)}


@server.tool()
def epistemic_stats() -> dict:
    all_claims = claim_store.all()
    total = len(all_claims)
    by_status = {}
    for s in EpistemicStatus.valid():
        by_status[s] = sum(1 for c in all_claims if c.status == s)
    by_domain = {}
    for d in claim_store.domains():
        by_domain[d] = len(claim_store.by_domain(d))
    avg_conf = sum(c.confidence for c in all_claims) / total if total else 0.0
    return {
        "total_claims": total,
        "by_status": by_status,
        "by_domain": by_domain,
        "avg_confidence": round(avg_conf, 4),
        "domains_count": len(by_domain),
    }


if __name__ == "__main__":
    server.run()
