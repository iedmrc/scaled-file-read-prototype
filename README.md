# Welcome to Clickhouse Case Solution 👋

A solution for Clickhouse case study developed by Ibrahim Demirci. 

## Install

```sh
docker build -t clickhouse-case .
```

## Usage

```sh
docker run -it --rm -v $(pwd)/input:/app/input clickhouse-case ./input/example.txt
```

or 

```sh
docker-compose up
```
## Run tests

```sh
docker run -it --rm -v $(pwd)/input:/app/input --entrypoint python clickhouse-case -m unittest discover tests
```

## Approach

My approach here is to maintain a `heapq` to store top N valued urls. If the values are the same, then Python's
`heappushpop()` method's default behavior resulted. (This behavior is a bit complicated)

## What's Next

- Tests can be further improved. Integration tests could be added.
- Parallelization can be done via a `ProcessPoolExecutor` to tackle the `GIL` bottleneck.
- When allowed, 3rd party libraries can enhance the capability of the project such as:
`typer` for argument parsing, `mypy` for better coding, `pytest` for better testing.
- When allowed `celery` can be used as a 3rd party tool to improve parallel process capabilities by
distributing to workers.
- OOP structre is defined well-enough but there are some rooms. I skip some of them to avoid overengineering.


## Author

👤 **Ibrahim Demirci**

* Website: https://ibrahim.demirci.com
* Github: [@iedmrc](https://github.com/iedmrc)