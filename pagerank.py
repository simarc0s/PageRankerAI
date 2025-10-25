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
    parser.add_argument("corpus", help="Directory containing the corpus HTML files")
    parser.add_argument("--csv", dest="csv", help="Output CSV file to save ranks (page,sampling_rank,iterate_rank)")
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


def iterate_pagerank(corpus, damping_factor):
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

        # Check convergence: max absolute difference < 0.001
        diff = max(abs(new_ranks[p] - ranks[p]) for p in pages)
        changed = diff >= 0.001
        ranks = new_ranks

    return ranks


if __name__ == "__main__":
    main()
