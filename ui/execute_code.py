import subprocess
import psutil


def execute_code(code, inp, expected_output, timeout=1, memory_limit_mb=256):
    try:
        # Получаем текущий процесс
        current_process = psutil.Process()

        # Получаем текущий лимит виртуальной памяти
        mem = current_process.memory_info().vms

        # Устанавливаем ограничение по памяти для текущего процесса
        if mem < memory_limit_mb * 1024 * 1024:
            result = subprocess.run(
                ["python", "-c", code],
                input=inp.encode(),
                # text=True,
                capture_output=True,
                timeout=timeout,
            )

            print(result.stdout)
            if result.returncode == 0:
                if result.stdout.decode().strip() == expected_output.strip():
                    return {"status": "Accepted", "output": result.stdout.decode().strip()}
                else:
                    return {
                        "status": "Wrong Answer",
                        "output": f"Expected output: ~{expected_output}~, Actual output: ~{result.stdout.decode().strip()}~",
                    }
            else:
                return {"status": "Compilation Error", "output": "Compilation error"}
        else:
            return {
                "status": "Memory limit",
                "output": f"Memory limit exceeded: {mem} bytes",
            }
    except subprocess.TimeoutExpired:
        return {"status": "Time limit", "output": "Time limit exceeded"}
    except Exception as e:
        return {"status": "Error", "output": str(e)}


# for i in range(5):
#     inp, out = [i.strip() for i in input().split()]
#     # print(inp, out)
#     print(execute_code(code="print(input())", inp=inp, expected_output=out))
