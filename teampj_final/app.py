from flask import Flask, render_template, request
import subprocess
import os
import sys
import json
from crawling.filter import filter_places

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/result')
def result():
    query = request.args.get('query')

    # 크롤링 실행
    try:
        subprocess.run([sys.executable, "crawling/crawler.py", query], check=True)
    except subprocess.CalledProcessError:
        return render_template(
            "result.html",
            results={}, 
            query=query, 
            error="예기치 못한 오류 발생"
        )

    # 결과 파일 경로
    JSON_PATH = os.path.join(app.root_path, 'result.json')
    if not os.path.exists(JSON_PATH):
        return render_template(
            "result.html",
            results={}, 
            query=query, 
            error="결과 파일이 존재하지 않습니다"
        )

    # 결과 로드
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        places = json.load(f)

    if not places:
        return render_template(
            "result.html",
            results={}, 
            query=query, 
            error=f"'{query}'에 대한 장소를 찾지 못했습니다"
        )

    # 필터링 후 dict 형태 유지
    filtered_data = filter_places(places)

    # 최종 렌더링: filtered_data 그대로 넘기기
    return render_template(
        'result.html',
        results=filtered_data,
        query=query,
        error=None
    )

if __name__ == '__main__':
    app.run(debug=True)