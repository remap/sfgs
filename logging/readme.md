### SFGS master logger

* Running instance

Flask backend on www.searchforglobalsong.com port 25000 (128.97.98.11:25000).

Tail log visualizer on http://128.97.98.11:25000/tail_log

* Logging schema

<pre>
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
</pre>

* Logging interfaces:

** Python logging: <a href="https://github.com/remap/sfgs/blob/master/logging/test.py">example code</a>

Can run with
<pre>
python test.py --server=128.97.98.11:25000 --url=/log/insert --name=zhehao --msg=log!
</pre>

In the code, can specify extra fields in each log message, 

** JSON logging, try in terminal: 
<pre>
curl -H "Content-type:application/json" --data @test.json http://128.97.98.11:25000/log/insert
</pre>
where test.json is the log entry <a href="https://github.com/remap/sfgs/blob/master/logging/test.json">example</a>.