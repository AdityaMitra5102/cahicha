#!/usr/bin/env python3
import sys
import requests
def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            token = line.strip()
            resp=requests.post('http://localhost:5000/validate', data={'token': token})
            print(resp.text)
            sys.stdout.flush()
            
        except Exception as e:
            print("invalid")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
