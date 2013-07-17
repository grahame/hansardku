create table haiku_search (poem_index integer primary key, haiku tsvector);
insert into haiku_search (poem_index, haiku) select poem_index, to_tsvector('english', talker || ' ' || poem) from haiku;
create index haiku_search_idx ON haiku_search using gin(haiku);
