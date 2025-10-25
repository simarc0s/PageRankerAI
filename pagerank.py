import argparse
import csv
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    parser = argparse.ArgumentParser(
        description="Compute PageRank for a corpus of HTML files."
    )
    parser.add_argument(
        "corpus",
        help="Directory containing the corpus HTML files",
    )
    parser.add_argument(
        "--csv",
        dest="csv",
        help="Output CSV file to save ranks (page,sampling_rank,iterate_rank)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare Sampling vs Iteration ranks and show differences",
    )
    parser.add_argument(
        "--diff-threshold",
        dest="diff_threshold",
        type=float,
        default=0.0,
        help="When using --compare, only show pages with abs(sampling-iterate) >= threshold (default: 0.0)",
    )
    parser.add_argument(
        "--topic-prefix",
        dest="topic_prefix",
        help="Comma-separated prefixes to build a personalized teleport vector (case-insensitive)",
    )
    args = parser.parse_args()

    corpus = crawl(args.corpus)

    sampling_ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(sampling_ranks):
        print(f"  {page}: {sampling_ranks[page]:.4f}")

    iterate_ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(iterate_ranks):
        print(f"  {page}: {iterate_ranks[page]:.4f}")

    if args.csv:
        try:
            with open(args.csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["page", "sampling_rank", "iterate_rank"])
                for page in sorted(corpus.keys()):
                    s = sampling_ranks.get(page, 0.0)
                    it = iterate_ranks.get(page, 0.0)
                    writer.writerow([page, f"{s:.6f}", f"{it:.6f}"])
            print(f"Ranks written to CSV: {args.csv}")
        except OSError as e:
            sys.exit(f"Error writing CSV file: {e}")

    # Optional comparison view
    if args.compare:
        print("\nComparison: Sampling vs Iteration")
        rows = []
        for page in corpus.keys():
            s = sampling_ranks.get(page, 0.0)
            it = iterate_ranks.get(page, 0.0)
            diff = abs(s - it)
            rows.append((page, s, it, diff))

        total_rows = len(rows)

        # Apply optional threshold filter
        threshold = args.diff_threshold if args.diff_threshold is not None else 0.0
        if threshold > 0.0:
            rows = [r for r in rows if r[3] >= threshold]

        # Sort by absolute difference descending
        rows.sort(key=lambda r: r[3], reverse=True)

        # Determine column widths
        page_w = max([len("page")] + [len(r[0]) for r in rows])
        header_note = (
            f" (threshold: {threshold:.6f}; shown {len(rows)}/{total_rows})"
            if threshold > 0.0
            else ""
        )
        header = (
            f"{'page'.ljust(page_w)}  "
            f"{'sampling':>10}  "
            f"{'iterate':>10}  "
            f"{'abs_diff':>10}{header_note}"
        )
        print(header)
        print("-" * len(header))
        if rows:
            for page, s, it, d in rows:
                print(f"{page.ljust(page_w)}  {s:>10.6f}  {it:>10.6f}  {d:>10.6f}")
        else:
            print("(no pages meet the threshold)")

        # Summary stats
        if total_rows:
            diffs = [r[3] for r in rows] if rows else [0.0]
            max_diff = max(diffs)
            mean_diff = sum(diffs) / len(diffs)
            print(f"\nSummary: max_diff = {max_diff:.6f}, mean_diff = {mean_diff:.6f}")

    # Optional: Personalized PageRank using topic-biased teleport
    if args.topic_prefix:
        raw = [p.strip().lower() for p in args.topic_prefix.split(",") if p.strip()]
        # Build teleport vector t: weight 1 if page name contains any prefix, else 0
        t = {p: 0.0 for p in corpus}
        for p in corpus:
            pl = p.lower()
            if any(pref in pl for pref in raw):
                t[p] = 1.0
        total = sum(t.values())
        if total <= 0:
            # Fallback to uniform if no matches
            n = len(corpus)
            t = {p: 1.0 / n for p in corpus}
            note = "(nenhuma página correspondeu; teleporte uniforme)"
        else:
            # Normalize to sum to 1
            t = {p: v / total for p, v in t.items()}
            note = ""

        personalized = iterate_pagerank(corpus, DAMPING, teleport=t)
        label = f"Personalized PageRank (prefixos: {args.topic_prefix})"
        print(label, note)
        for page in sorted(personalized):
            print(f"  {page}: {personalized[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Number of pages in the corpus
    N = len(corpus)

    # If the page has no outgoing links (dangling), treat as linking to all pages uniformly
    links = corpus.get(page, set())
    if not links:
        return {p: 1 / N for p in corpus}

    # Base probability for jumping to any page
    base = (1 - damping_factor) / N

    # Probability mass distributed among linked pages
    linked_share = damping_factor / len(links)

    distribution = {}
    for p in corpus:
        distribution[p] = base
        if p in links:
            distribution[p] += linked_share

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize counts for each page
    counts = {p: 0 for p in corpus}

    # Start from a random page
    current = random.choice(list(corpus.keys()))

    # Perform n samples
    for _ in range(n):
        # Count visit to current page
        counts[current] += 1

        # Get transition probabilities from current page
        dist = transition_model(corpus, current, damping_factor)

        # Sample next page according to distribution
        pages = list(dist.keys())
        weights = list(dist.values())
        current = random.choices(pages, weights=weights, k=1)[0]

    # Convert counts to probabilities (normalize by n)
    ranks = {p: counts[p] / n for p in counts}

    return ranks


def iterate_pagerank(corpus, damping_factor, teleport=None):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pages = list(corpus.keys())

    # Initialize ranks uniformly
    ranks = {p: 1 / N for p in pages}

    # Precompute incoming links for efficiency
    incoming = {p: set() for p in pages}
    for src, outs in corpus.items():
        for dst in outs:
            if dst in incoming:
                incoming[dst].add(src)

    # Iterate until convergence
    changed = True
    while changed:
        new_ranks = {}

        # Total rank from dangling pages (no outgoing links)
        dangling_sum = sum(ranks[p] for p in pages if len(corpus[p]) == 0)

        if teleport is None:
            # Classic uniform teleportation
            for p in pages:
                # Base teleportation component
                pr = (1 - damping_factor) / N

                # Contribution from dangling pages distributed uniformly
                pr += damping_factor * (dangling_sum / N)

                # Contributions from pages that link to p
                link_sum = 0.0
                for q in incoming[p]:
                    Lq = len(corpus[q]) if len(corpus[q]) > 0 else N
                    link_sum += ranks[q] / Lq
                pr += damping_factor * link_sum

                new_ranks[p] = pr
        else:
            # Personalized teleport vector (must sum to 1 across pages)
            # Ensure teleport has entries for all pages and is normalized
            total_t = sum(teleport.get(p, 0.0) for p in pages)
            if total_t <= 0:
                total_t = 1.0
                t = {p: 1.0 / N for p in pages}
            else:
                t = {p: teleport.get(p, 0.0) / total_t for p in pages}

            for p in pages:
                # Base teleportation component according to t
                pr = (1 - damping_factor) * t[p]

                # Contribution from dangling pages distributed according to t
                pr += damping_factor * dangling_sum * t[p]

                # Contributions from pages that link to p
                link_sum = 0.0
                for q in incoming[p]:
                    Lq = len(corpus[q]) if len(corpus[q]) > 0 else N
                    link_sum += ranks[q] / Lq
                pr += damping_factor * link_sum

                new_ranks[p] = pr

        # Check convergence: max absolute difference < 0.001
        diff = max(abs(new_ranks[p] - ranks[p]) for p in pages)
        changed = diff >= 0.001
        ranks = new_ranks

    return ranks


if __name__ == "__main__":
    main()
