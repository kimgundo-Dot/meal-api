import pandas as pd
import itertools

# CSV 파일 읽기 (인코딩은 한컴오피스 기준 cp949)
rice_df = pd.read_csv("rice.csv", encoding="cp949")
side_df = pd.read_csv("side.csv", encoding="cp949")
soup_df = pd.read_csv("soup.csv", encoding="cp949")

# 사용자 입력 (태그 필터)
user_tags = ['쌀밥', '닭고기', '담백함', '매움']

# 추천 리스트 초기화
recommendations = []

# 모든 밥-반찬-국 조합 반복
for rice, side, soup in itertools.product(rice_df.itertuples(), side_df.itertuples(), soup_df.itertuples()):
    try:
        # 총 칼로리 계산
        kcal_sum = float(rice.칼로리) + float(side.칼로리) + float(soup.칼로리)
    except:
        continue

    # 칼로리 범위 필터 (너무 빡세지 않게 여유 줌)
    if 500 <= kcal_sum <= 1500:
        try:
            tags_r = [tag.strip() for tag in str(rice.태그).split(',') if tag and str(tag).lower() != 'nan']
            tags_s = [tag.strip() for tag in str(side.태그).split(',') if tag and str(tag).lower() != 'nan']
            tags_k = [tag.strip() for tag in str(soup.태그).split(',') if tag and str(tag).lower() != 'nan']
        except:
            continue

        all_tags = set(tags_r + tags_s + tags_k)
        match_score = len(set(user_tags) & all_tags) / len(user_tags)

        recommendations.append({
            "밥": rice.음식명,
            "반찬": side.음식명,
            "국": soup.음식명,
            "칼로리": round(kcal_sum, 1),
            "점수": round(match_score, 2),
            "세트태그": list(all_tags)
        })

# 점수순 정렬
recommendations = sorted(recommendations, key=lambda x: x["점수"], reverse=True)

# 출력
if not recommendations:
    print("⚠️ 조건에 맞는 식단이 없습니다. 태그를 줄이거나 칼로리 범위를 넓혀보세요.")
else:
    for r in recommendations[:3]:
        print("\n🍱 추천 세트")
        print(f"- 밥: {r['밥']}")
        print(f"- 반찬: {r['반찬']}")
        print(f"- 국: {r['국']}")
        print(f"- 총 칼로리: {r['칼로리']} kcal")
        print(f"- 유사도 점수: {r['점수']}점")
        print(f"- 태그: {r['세트태그']}")
