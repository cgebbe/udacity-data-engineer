import utils


examples = dict()
examples[
    "top10_songs"
] = """
SELECT s.title, a.name, COUNT(*) AS play_count
FROM songplays sp
JOIN songs s ON sp.song_id = s.song_id
JOIN artists a ON sp.artist_id = a.artist_id
GROUP BY s.title, a.name
ORDER BY play_count DESC
LIMIT 10;
"""
examples[
    "active_user_count_per_week"
] = """
SELECT t.week, COUNT(DISTINCT sp.user_id) AS active_users
FROM songplays sp
JOIN time t ON sp.start_time = t.start_time
GROUP BY t.week
ORDER BY t.week;
"""
examples[
    "gender_distribution"
] = """
SELECT u.gender, COUNT(*) AS user_count
FROM users u
GROUP BY u.gender;
"""


def main():
    with utils.Connection() as conn:
        # conn.run(query)
        for k, v in examples.items():
            print(f"### {k.upper()}")
            conn.run(v)


if __name__ == "__main__":
    main()
