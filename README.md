# Geography of Deletion
This repository provides a set of SQL and utilities for extracting information
about deleted pages.

## Step 1 -- Extract deleted article metadata

    cat sql/deleted_last_revision.sql | \
    mysql <... args ...> > \
    datasets/deleted_last_revision.tsv

This will produce a dataset of deleted articles with the last rev_id and some
other metdata.

## Step 2 -- Fetch text for deleted articles

    cat datasets/deleted_last_revision.tsv | \
    ./fetch_text --api=https://en.wikipedia.org/w/api.php --check-deleted-first > \
    datasets/deleted_last_text.tsv

This will add a 'last_text' column to the dataset containing the text of the
last revision of the article.
