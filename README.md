# python-ai-course
### Completing AI task using python as on boarding training

-- run hash-tag `python app.py` 

-- apply curl script:
#### Hash-tag
```
curl -X POST http://localhost:5000/process \
-H 'Content-Type: application/json' \
-d '{"text": "Let us focus on eating more natural and artificial products."}'
```

#### Add more keyword
```
curl -X POST http://localhost:5000/keyword \
-H 'Content-Type: application/json' \
-d '{"keyword": "healthy"}'
```

#### Using elastic search
```
curl -X POST http://localhost:5000/process -H 'Content-Type: application/json' -d '{"text": "Explore natural solutions and artificial intelligence."}'
```
-- and
```
curl -X POST http://localhost:5000/keyword -H 'Content-Type: application/json' -d '{"keyword": "artificial"}'
```
