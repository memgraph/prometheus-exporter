import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics_response import parse_json_metrics


class FakeResponse:
    def __init__(self, json_value=None, json_exc=None, text="", headers=None):
        self._json_value = json_value
        self._json_exc = json_exc
        self.text = text
        self.headers = headers or {}

    def json(self):
        if self._json_exc is not None:
            raise self._json_exc
        return self._json_value


def test_returns_parsed_json_on_valid_body():
    res = FakeResponse(json_value={"General": {"vertex_count": 1}})
    assert parse_json_metrics(res, "http://mg:9091") == {"General": {"vertex_count": 1}}


def test_openmetrics_body_raises_actionable_error():
    res = FakeResponse(
        json_exc=ValueError("Expecting value: line 1 column 1 (char 0)"),
        text="# HELP memgraph_vertex_count ...\n# TYPE ...\n",
        headers={"Content-Type": "text/plain; version=0.0.4"},
    )
    try:
        parse_json_metrics(res, "http://mg:9091")
    except ValueError as e:
        msg = str(e)
    else:
        raise AssertionError("expected ValueError")
    assert "OpenMetrics" in msg
    assert "--metrics-format=OpenMetrics" in msg
    assert "http://mg:9091" in msg


def test_other_non_json_raises_generic_error():
    res = FakeResponse(
        json_exc=ValueError("Expecting value: line 1 column 1 (char 0)"),
        text="<html>oops</html>",
        headers={"Content-Type": "text/html"},
    )
    try:
        parse_json_metrics(res, "http://mg:9091")
    except ValueError as e:
        msg = str(e)
    else:
        raise AssertionError("expected ValueError")
    assert "non-JSON" in msg
    assert "OpenMetrics" not in msg


if __name__ == "__main__":
    import traceback

    failures = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"PASS {_name}")
            except Exception:
                failures += 1
                print(f"FAIL {_name}")
                traceback.print_exc()
    print(f"\n{failures} failure(s)")
    sys.exit(1 if failures else 0)
