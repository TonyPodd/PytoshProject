import requests
import time

def send(id, code, inp, out):
    url = "https://judge0-extra-ce.p.rapidapi.com/submissions"

    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": "eec5b2ff0amshb3bdf983da56557p1c42f4jsn12b7a318a554",
        "X-RapidAPI-Host": "judge0-extra-ce.p.rapidapi.com",
    }


    data = {
        "source_code": code,
        "language_id": id,
        "stdin": inp,
        "expected_output": out,
        "time_limit": 1000,
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  
        
        token = response.json()["token"]

        url_check = f"https://judge0-extra-ce.p.rapidapi.com/submissions/{token}"

        headers_check = {
            "X-RapidAPI-Key": "1486fb1c99msh3ba6053825cd70cp17df4ajsnb817881eb21b",
            "X-RapidAPI-Host": "judge0-extra-ce.p.rapidapi.com",
        }

        start_time = time.time() 

        while True:
            response_check = requests.get(url_check, headers=headers_check)
            result = response_check.json()

            status = result["status"]["description"]
            output = result["stdout"]
            
            if status not in ['In Queue', 'Processing']:
                return {'status': status, 'output': output}
            
            if time.time() - start_time > 10:
                return {'status': 'Error', 'output': 'Time limit exceeded'}
            
            time.sleep(0.1)

    except requests.exceptions.RequestException as e:
        return {'status': 'Error', 'output': str(e)}

if __name__ == "__main__":
    data = send(25, "print(int(input()) + 1)", "1", "2")
    print(data)
