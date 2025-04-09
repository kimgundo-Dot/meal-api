from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import itertools
import random
import os

app = Flask(__name__)
CORS(app)

# 🔁 CSV 로딩 함수 (인코딩 자동 처리)
def load_csv(path):
    try:
        return pd.read_csv(path, encoding='cp949')
    except:
        return pd.read_csv(path, encoding='utf-8-sig')

# 📦 CSV 데이터 로드
base_path = os.path.dirname(__file__)
rice_df = load_csv(os.path.join(base_path, "rice.csv"))
side_df = load_csv(os.path.join(base_path, "side.csv"))
soup_df = load_csv(os.path.join(base_path, "soup.csv"))

# ⭐ 추천 알고리즘 함수
def recommend_meals(user_tags):
    meal_sets = {"아침": [], "점심": [], "저녁": []}

    for meal_time in meal_sets:
        candidates = []

        for rice, side, soup in itertools.product(rice_df.itertuples(), side_df.itertuples(), soup_df.itertuples()):
            try:
                kcal_sum = rice.에너지 + side.에너지 + soup.에너지
                if not (550 <= kcal_sum <= 750):
                    continue

                tags_r = (str(rice.맛태그) + ',' + str(rice.재료태그)).split(',')
                tags_s = (str(side.맛태그) + ',' + str(side.재료태그)).split(',')
                tags_k = (str(soup.맛태그) + ',' + str(soup.재료태그)).split(',')

                all_tags = set(tag.strip() for tag in tags_r + tags_s + tags_k if tag and tag.lower() != 'nan')
                match_score = len(set(user_tags) & all_tags) / len(user_tags) if user_tags else 0

                candidates.append({
                    "밥": rice.식품명,
                    "반찬": side.식품명,
                    "국": soup.식품명,
                    "칼로리": round(kcal_sum, 1),
                    "점수": round(match_score, 2),
                    "세트태그": list(all_tags)
                })

            except Exception as e:
                continue

        if candidates:
            sorted_candidates = sorted(candidates, key=lambda x: x["점수"], reverse=True)
            meal_sets[meal_time] = random.choice(sorted_candidates[:5])

    return meal_sets

# 📡 추천 요청 받는 API
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json(force=True)
        user_tags = data.get("tags", [])
        user_tags = [tag.replace("함", "") if tag.endswith("함") else tag for tag in user_tags]

        print("📥 받은 태그:", user_tags)

        result = recommend_meals(user_tags)

        if not any(result.values()):
            return jsonify({"message": "⚠️ 조건에 맞는 식단이 없습니다."}), 200

        return jsonify(result), 200

    except Exception as e:
        print("❌ 오류:", e)
        return jsonify({"error": "서버 오류가 발생했습니다."}), 500

# 🛠️ 루트 접속 안내
@app.route('/', methods=['GET'])
def home():
    return "🥣 자동 식단 추천 Flask 서버입니다. POST /recommend 로 요청해주세요."

# 🚀 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
