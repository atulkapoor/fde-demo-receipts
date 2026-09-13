# Implementation log

## Round 1

- check: red
- changed: app/components/perception.py, app/components/representation.py

```
metrics: field_exact_match, field_coverage
  golden         84 cases  59.5%
               by source: {'prediction': 34}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 2

- check: red
- changed: app/components/evaluation.py

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 3

- check: red

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 4

- check: red
- changed: app/components/representation.py

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 5

- check: red

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 6

- check: red
- changed: app/components/perception.py, app/components/representation.py

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

## Round 7

- check: red

```
metrics: field_exact_match, field_coverage
  golden         84 cases  72.6%
               by source: {'prediction': 23}
  edge_case       0 cases  --
  adversarial     2 cases  100.0%
below 85.0%
```

**Stopped by**: round cap.
