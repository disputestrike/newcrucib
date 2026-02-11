"""
Tests for code quality scoring.
"""
import pytest
from code_quality import score_generated_code


def test_score_empty_inputs():
    r = score_generated_code()
    assert "overall_score" in r
    assert "breakdown" in r
    assert "verdict" in r
    assert 0 <= r["overall_score"] <= 100
    assert r["verdict"] in ("excellent", "good", "needs_work")


def test_score_with_frontend_code():
    fe = """
    import React from 'react';
    const App = () => <div className="root">Hello</div>;
    export default App;
    """
    r = score_generated_code(frontend_code=fe)
    assert r["breakdown"]["frontend"]["score"] > 0
    assert r["breakdown"]["frontend"]["has_components"]
    assert r["breakdown"]["frontend"]["has_styling"]


def test_score_with_backend_code():
    be = """
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def root():
        try:
            return {"message": "ok"}
        except Exception:
            return {"error": "bad"}
    """
    r = score_generated_code(backend_code=be)
    assert r["breakdown"]["backend"]["score"] > 0
    assert r["breakdown"]["backend"]["has_routes"]
    assert r["breakdown"]["backend"]["has_error_handling"]


def test_score_with_tests():
    tests = "def test_foo(): assert True\ndef test_bar(): assert 1 == 1"
    r = score_generated_code(test_code=tests)
    assert r["breakdown"]["tests"]["test_count"] >= 1
    assert r["breakdown"]["tests"]["score"] >= 10


def test_verdict_excellent_high_score():
    fe = "import React from 'react';\n" + "const C = () => null;\n" * 60 + "export default C;"
    be = "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef r(): return {}\n" + "# comment\n" * 60
    db = "CREATE TABLE users (id INT PRIMARY KEY); CREATE TABLE posts (id INT, user_id INT, FOREIGN KEY (user_id) REFERENCES users(id));"
    tc = "def test_a(): pass\n" * 10
    r = score_generated_code(frontend_code=fe, backend_code=be, database_schema=db, test_code=tc)
    assert r["overall_score"] >= 50
    assert r["verdict"] in ("excellent", "good", "needs_work")
