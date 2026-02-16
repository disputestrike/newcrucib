"""
Tests for code_executor.py
"""
import pytest
from code_executor import CodeExecutor


@pytest.mark.asyncio
async def test_validate_frontend_success():
    """Test successful frontend validation"""
    executor = CodeExecutor()
    files = {
        "package.json": '''{
            "name": "test",
            "version": "1.0.0",
            "scripts": {
                "build": "echo 'Build successful'"
            }
        }''',
        "src/App.tsx": "export default function App() { return <div>Hi</div> }"
    }
    result = await executor.validate_frontend(files)
    assert result["valid"] is True
    assert result["stage"] == "success"
    assert result["error"] is None


@pytest.mark.asyncio
async def test_validate_frontend_no_package_json():
    """Test frontend validation without package.json"""
    executor = CodeExecutor()
    files = {
        "src/App.tsx": "export default function App() { return <div>Hi</div> }"
    }
    result = await executor.validate_frontend(files)
    assert result["valid"] is False
    assert result["stage"] == "validation"
    assert "package.json" in result["error"]


@pytest.mark.asyncio
async def test_validate_frontend_build_failure():
    """Test frontend validation with build failure"""
    executor = CodeExecutor()
    files = {
        "package.json": '''{
            "name": "test",
            "version": "1.0.0",
            "scripts": {
                "build": "exit 1"
            }
        }'''
    }
    result = await executor.validate_frontend(files)
    assert result["valid"] is False
    assert result["stage"] == "build"
    assert result["error"] is not None


@pytest.mark.asyncio
async def test_validate_backend_python_valid():
    """Test valid Python backend validation"""
    executor = CodeExecutor()
    files = {
        "main.py": '''
def hello():
    return "world"

if __name__ == "__main__":
    print(hello())
''',
        "utils.py": '''
def add(a, b):
    return a + b
'''
    }
    result = await executor.validate_backend(files, "Python")
    assert result["valid"] is True
    assert result["stage"] == "success"
    assert result["files_checked"] == 2


@pytest.mark.asyncio
async def test_validate_backend_python_syntax_error():
    """Test Python backend with syntax error"""
    executor = CodeExecutor()
    files = {
        "main.py": '''
def hello(
    return "world"
'''
    }
    result = await executor.validate_backend(files, "Python")
    assert result["valid"] is False
    assert result["stage"] == "syntax"
    assert "main.py" in result["error"]


@pytest.mark.asyncio
async def test_validate_backend_python_empty():
    """Test Python backend with no Python files"""
    executor = CodeExecutor()
    files = {
        "README.md": "# Test Project"
    }
    result = await executor.validate_backend(files, "Python")
    assert result["valid"] is True
    assert result["files_checked"] == 0


@pytest.mark.asyncio
async def test_run_tests_basic():
    """Test basic test execution"""
    executor = CodeExecutor()
    files = {
        "main.py": "def add(a, b): return a + b",
        "test_main.py": '''
def test_add():
    from main import add
    assert add(1, 2) == 3
'''
    }
    result = await executor.run_tests(files, "python -m pytest -v", "Python")
    # Result should have structure even if tests fail due to missing pytest
    assert "passed" in result
    assert "duration" in result
    assert "stdout" in result
    assert "stderr" in result


@pytest.mark.asyncio
async def test_run_command_success():
    """Test successful command execution"""
    executor = CodeExecutor()
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    try:
        result = await executor._run_command(["echo", "hello"], temp_dir, timeout=5)
        assert result["returncode"] == 0
        assert "hello" in result["stdout"]
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_run_command_failure():
    """Test command execution failure"""
    executor = CodeExecutor()
    import tempfile
    import os
    
    temp_dir = tempfile.mkdtemp()
    try:
        result = await executor._run_command(["false"], temp_dir, timeout=5)
        assert result["returncode"] != 0
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_run_command_timeout():
    """Test command execution timeout"""
    executor = CodeExecutor(timeout=2)
    import tempfile
    import os
    import asyncio
    
    temp_dir = tempfile.mkdtemp()
    try:
        with pytest.raises(asyncio.TimeoutError):
            await executor._run_command(["sleep", "10"], temp_dir, timeout=1)
    finally:
        import shutil
        shutil.rmtree(temp_dir)


@pytest.mark.asyncio
async def test_validate_frontend_error_handling():
    """Test frontend validation error handling"""
    executor = CodeExecutor()
    # Pass invalid files structure that will cause an error
    files = None
    try:
        result = await executor.validate_frontend(files)
        assert result["valid"] is False
        assert "error" in result
    except Exception:
        # Exception handling in validate_frontend should prevent this
        pytest.fail("validate_frontend should handle errors gracefully")


@pytest.mark.asyncio
async def test_validate_backend_unsupported_language():
    """Test backend validation with unsupported language"""
    executor = CodeExecutor()
    files = {
        "main.rb": "puts 'Hello World'"
    }
    result = await executor.validate_backend(files, "Ruby")
    assert result["valid"] is False
    assert "Unsupported" in result["error"]
