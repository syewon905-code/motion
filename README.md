# Motion

30초 16:9(1920×1080, 30fps) 모션 그래픽 영상과 생성 코드.

## new-year-2027 — 2027 신년 인사 영상
| 파일 | 설명 |
|---|---|
| `happy_new_year_2027_30s_v4_christmas.mp4` | **최종본** — v2 기반, 초록·하양·빨강 크리스마스 컬러 |
| `happy_new_year_2027_30s_v2.mp4` | 장면 중심 다이나믹 버전 (마을 · 트리/머그/선물 · 시계 카운트다운 · 불꽃놀이 · 건배) |
| `happy_new_year_2027_30s_v3_kitsch.mp4` | 키치 스타일 + 나눔고딕 ExtraBold |
| `happy_new_year_2027_30s.mp4` | v1 타이포그래피 버전 |

음악은 직접 합성한 오리지널 캐롤풍 왈츠(첼레스타·종·썰매방울)라 저작권 문제가 없습니다.

## pepsi-zero — 제로 콜라 컨셉 광고 시안
`pepsi_zero_ad_30s.mp4` — 키네틱 타이포그래피 + 직접 그린 캔 + 합성 BGM (공식 이미지 미사용 시안)

## 다시 렌더링하기
Python 3, Pillow, NumPy, ffmpeg 필요. v3는 `fonts-nanum` 필요.
```bash
cd new-year-2027/src
python3 music_v2.py
python3 render_v4_christmas.py
ffmpeg -framerate 30 -i frames4/f%04d.jpg -i music.wav -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -shortest out.mp4
```
