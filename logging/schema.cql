CREATE KEYSPACE IF NOT EXISTS s4gs WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'datacenter1': '1'
};

USE s4gs;

CREATE TABLE IF NOT EXISTS log (
  event_id          timeuuid,
  time              timestamp,
  level             int,        
  user              text,
  module            text,
  log               text,
  associated_object text,
  host              text,
  pid               int,
  
  PRIMARY KEY (module, event_id)
) with clustering order by (event_id ASC);



CREATE TABLE IF NOT EXISTS users (
  email text,
  aff text,
  created_by text,
  created_on text,
  first_name text,
  gdrive text,
  ip text,
  last_name text,
  location text,
  password text,
  script_coverage text,
  script_progress int,
  shots_count int,
  status text,
  updated_on text,
  url_gplus text,
  url_yt text,
  user_type text,
  videos_count int,
  website text,
  PRIMARY KEY (email)
) WITH COMPACT STORAGE AND
  bloom_filter_fp_chance=0.010000 AND
  caching='{"keys":"ALL", "rows_per_partition":"NONE"}' AND
  comment='' AND
  dclocal_read_repair_chance=0.100000 AND
  gc_grace_seconds=864000 AND
  read_repair_chance=0.000000 AND
  default_time_to_live=0 AND
  speculative_retry='99.0PERCENTILE' AND
  memtable_flush_period_in_ms=0 AND
  compaction={'class': 'SizeTieredCompactionStrategy'} AND
  compression={'sstable_compression': 'LZ4Compressor'};

CREATE TABLE IF NOT EXISTS wp_emails (
  wp_email text,
  email text,
  PRIMARY KEY (wp_email)
) WITH COMPACT STORAGE AND
  bloom_filter_fp_chance=0.010000 AND
  caching='{"keys":"ALL", "rows_per_partition":"NONE"}' AND
  comment='' AND
  dclocal_read_repair_chance=0.100000 AND
  gc_grace_seconds=864000 AND
  read_repair_chance=0.000000 AND
  default_time_to_live=0 AND
  speculative_retry='99.0PERCENTILE' AND
  memtable_flush_period_in_ms=0 AND
  compaction={'class': 'SizeTieredCompactionStrategy'} AND
  compression={'sstable_compression': 'LZ4Compressor'};

CREATE TABLE IF NOT EXISTS yttokens (
  username text,
  access_token text,
  channel_id text,
  channel_name text,
  created text,
  expires_in text,
  refresh_token text,
  token_type text,
  PRIMARY KEY (username)
) WITH COMPACT STORAGE AND
  bloom_filter_fp_chance=0.010000 AND
  caching='{"keys":"ALL", "rows_per_partition":"NONE"}' AND
  comment='' AND
  dclocal_read_repair_chance=0.100000 AND
  gc_grace_seconds=864000 AND
  read_repair_chance=0.000000 AND
  default_time_to_live=0 AND
  speculative_retry='99.0PERCENTILE' AND
  memtable_flush_period_in_ms=0 AND
  compaction={'class': 'SizeTieredCompactionStrategy'} AND
  compression={'sstable_compression': 'LZ4Compressor'};