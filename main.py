import subprocess
import sys
import tempfile
import re
import difflib
import builtins

from pathlib import Path


def execute_code(code):

    with tempfile.TemporaryDirectory() as temp_dir:

        file_path = Path(temp_dir) / "sample.py"

        file_path.write_text(code)

        try:

            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=temp_dir
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }

        except subprocess.TimeoutExpired:

            return {
                "success": False,
                "output": "",
                "error": "Execution timed out"
            }


def analyze_error(error_message):

    match = re.search(
        r"name '(\w+)' is not defined",
        error_message
    )

    if not match:
        return None

    incorrect_name = match.group(1)

    suggestions = difflib.get_close_matches(
        incorrect_name,
        dir(builtins),
        n=1,
        cutoff=0.6
    )

    if suggestions:
        return incorrect_name, suggestions[0]

    return None


def fix_code(code, correction):

    incorrect_name, correct_name = correction

    pattern = r"\b" + re.escape(incorrect_name) + r"\b"

    return re.sub(pattern, correct_name, code)


def validate_result(result, expected_output):

    if not result["success"]:
        return False

    return (
        result["output"].strip()
        == expected_output
    )


def run_harness(code, expected_output, max_retries=2):

    attempt = 0

    while attempt <= max_retries:

        print(f"\nAttempt: {attempt + 1}")

        result = execute_code(code)

        if result["success"]:

            print("Code executed successfully!")

            if validate_result(result, expected_output):

                print("Validation successful!")

                return {
                    "success": True,
                    "code": code,
                    "output": result["output"]
                }

            print("Output validation failed.")
            break

        print("Execution failed.")
        print("Analyzing error...")

        correction = analyze_error(result["error"])

        if not correction:

            print("No automatic correction found.")
            break

        print("Suggested correction:", correction)

        code = fix_code(code, correction)

        attempt += 1

    return {
        "success": False,
        "code": code,
        "output": ""
    }


if __name__ == "__main__":

    buggy_code = (
        'pritn("Hello from AI Harness Engineering!")'
    )

    expected_output = (
        "Hello from AI Harness Engineering!"
    )

    final_result = run_harness(
        buggy_code,
        expected_output
    )

    print("\n========== FINAL RESULT ==========")

    print("Success:", final_result["success"])

    print("Final Code:")
    print(final_result["code"])

    print("Final Output:")
    print(final_result["output"])
