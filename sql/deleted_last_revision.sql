SELECT
  ar_page_id AS page_id,
  ar_namespace AS page_namespace,
  ar_title AS page_title,
  MAX(ar_rev_id) AS last_rev_id,
  MAX(ar_timestamp) AS last_timestamp,
  True AS archived
FROM archive
GROUP BY 1,2,3;
