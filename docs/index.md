<h1 align="center" style="vertical-align: middle;">
  <img src="./img/black.svg" width="30"> <strong>FastHealthcheck</strong>
</h1>

<b>Framework agnostic health checks with integrations for most popular ASGI frameworks: [FastAPI](https://github.com/fastapi/fastapi) / [Faststream](https://github.com/airtai/faststream) / [Litestar](https://github.com/litestar-org/litestar) to help you to implement the [Health Check API](https://microservices.io/patterns/observability/health-check-api.html) pattern</b>

---

## Installation

With `pip`:
```bash
pip install fast-healthcheck
```

With `poetry`:
```bash
poetry add fast-healthcheck
```

With `uv`:
```bash
uv add fast-healthcheck
```

## Usage

The easier way to use this package is to use the **`health`** function.

Create the health check endpoint dynamically using different conditions.
Each condition is a callable, and you can even have dependencies inside of it:

=== "examples/probes.py"

    ```python
    {%
        include-markdown "../examples/probes.py"
    %}
    ```

=== "FastAPI"

    ```python
    {%
        include-markdown "../examples/fastapi_example/main.py"
    %}
    ```

=== "Faststream"

    ```python
    {%
        include-markdown "../examples/faststream_example/main.py"
    %}
    ```

=== "Litestar"

    ```python
    {%
        include-markdown "../examples/litestar_example/main.py"
    %}
    ```

You can find examples for each framework here:

- [FastAPI example](./examples/fastapi_example)
- [Faststream example](./examples/faststream_example)
- [Litestar example](./examples/litestar_example)
