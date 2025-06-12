# crawling/filter.py

import json
from collections import Counter
from soynlp.tokenizer import RegexTokenizer

# 테마 키워드 정의
keyword = {
    "힐링": ['자연', '산책', '풍경', '경치', '뷰', '공원', '야경', '조용', '편안', '휴식', '쉼', '명상', '여유', '숲', '바람', '하늘', '잔잔','고요','한적'],
    "여름": ['바다', '해수욕', '물놀이', '해변', '모래사장', '계곡', '수영', '파라솔', '서핑','섬', '보트','요트','스노클링','다이빙','수상레저','햇살'],
    "맛집": ['맛있', '잘먹', '맛집', '요리', '식사', '음식', '한끼', '먹방', '풍미', '입맛', '요리법'],
    "모임": ['단체', '모임', '회식', '친구', '모여', '단체석', '예약', '단체룸','파티','함께'],
    "데이트": ['커플', '분위기', '로맨틱', '산책', '전망', '야경', '데이트', '조명', '감성','예쁜','아늑한','둘만의','기념일'],
    "가족": ['아이', '어린이', '부모', '어르신', '놀이공원', '체험', '가족', '유모차', '휴양','나들이','소풍','추억'],
    "액티비티": ['레저', '체험', '스릴', '놀이', '클라이밍', '집라인', '서바이벌', '짚라인', '승마', 'ATV','카트','패러글라이딩','번지점프','트레킹','하이킹','자전거'],
    "문화예술": ['미술관', '박물관', '전시', '예술', '공연', '전시회', '문화', '관람','역사','유적지','건축','음악','연극','영화','갤러리'],
    "사진": ['포토존', '인생샷', '감성샷', '사진', '찍기좋', '뷰맛집', '카메라','색감','구도','조명','배경','추억'],
    "야경": ['야경', '불빛', '야시장', '조명', '전망대', '야간', '밤', '빛','낭만적인','루프탑','스카이라운지']
}

tokenizer = RegexTokenizer()

#  테마 분석 함수
def filter_places(data):
    for place_name, info in data.items():
        if "themes" in info and len(info["themes"]) >= 1:
            continue

        review_list = info.get("review", [])
        tokens = []
        for review in review_list:
            tokens += tokenizer.tokenize(review, flatten=True)

        theme_count = Counter()
        for theme, keywords in keyword.items():
            if any(kw in token for token in tokens for kw in keywords):
                theme_count[theme] += 1

        top_themes = [theme for theme, _ in theme_count.most_common(3)]
        info["themes"] = top_themes

    # 분석 결과 저장 (디버깅용)
    with open("tag_analysis.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data
