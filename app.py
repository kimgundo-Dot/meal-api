from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import itertools
import random

app = Flask(__name__)
CORS(app)

# 🔁 인코딩 자동 처리 함수
def load_csv(path):
    try:
        return pd.read_csv(path, encoding='cp949')
    except:
        return pd.read_csv(path, encoding='utf-8-sig')

# 📦 CSV 로딩
rice_df = load_csv("rice.csv")
side_df = load_csv("side.csv")
soup_df = load_csv("soup.csv")

# ⭐ 추천 알고리즘 함수
def recommend_meals(user_tags):
    meal_sets = {"아침": [], "점심": [], "저녁": []}

    for meal_time in meal_sets:
        candidates = []

        for rice, side, soup in itertools.product(rice_df.itertuples(), side_df.itertuples(), soup_df.itertuples()):
            try:
                kcal_sum = rice.에너지 + side.에너지 + soup.에너지
            except:
                continue

            if 550 <= kcal_sum <= 750:
                try:
                    tags_r = (str(rice.맛태그) + ',' + str(rice.재료태그)).split(',')
                    tags_s = (str(side.맛태그) + ',' + str(side.재료태그)).split(',')
                    tags_k = (str(soup.맛태그) + ',' + str(soup.재료태그)).split(',')
                except:
                    continue

                all_tags = set([tag.strip() for tag in tags_r + tags_s + tags_k if tag and tag.lower() != 'nan'])
                match_score = len(set(user_tags) & all_tags) / len(user_tags) if user_tags else 0

                candidates.append({
                    "밥": rice.식품명,
                    "반찬": side.식품명,
                    "국": soup.식품명,
                    "칼로리": round(kcal_sum, 1),
                    "점수": round(match_score, 2),
                    "세트태그": list(all_tags)
                })

        # 🎯 무조건 추천 보장: 점수순 정렬 후 상위 5개 중 랜덤 선택
        if candidates:
            sorted_candidates = sorted(candidates, key=lambda x: x["점수"], reverse=True)
            meal_sets[meal_time] = random.choice(sorted_candidates[:5])  # 점수 0이어도 포함

    return meal_sets

# 📡 Flask 라우팅
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_tags = data.get("tags", [])

    user_tags = [tag.replace("함", "") if tag.endswith("함") else tag for tag in user_tags]


    print("📥 받은 태그:", user_tags)

    result = recommend_meals(user_tags)

    # ❌ 결과가 완전 비었을 경우 (진짜 아무 조합도 없을 때)
    if not any(result.values()):
        return jsonify({"message": "⚠️ 조건에 맞는 식단이 없습니다."}), 200

    return jsonify(result), 200

# 🚀 실행
if __name__ == '__main__':
    app.run(debug=True)
