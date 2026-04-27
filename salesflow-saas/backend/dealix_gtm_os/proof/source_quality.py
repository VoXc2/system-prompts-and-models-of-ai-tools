"""Source quality — rates the reliability of evidence sources."""
SOURCE_RATINGS = {
    "company_website": 0.8,
    "uploaded_file": 0.9,
    "google_search": 0.6,
    "tavily": 0.7,
    "manual_input": 1.0,
    "llm_inference": 0.4,
    "mock": 0.3,
    "unknown": 0.1,
}

def rate_source(source_type: str) -> float:
    return SOURCE_RATINGS.get(source_type, 0.2)

def rate_sources(sources: list[str]) -> dict:
    if not sources:
        return {"average_quality": 0.0, "best_source": None, "count": 0}
    ratings = [rate_source(s) for s in sources]
    return {"average_quality": round(sum(ratings) / len(ratings), 2), "best_source": sources[ratings.index(max(ratings))], "count": len(sources)}
