# why e.page?
```sql
SELECT page, COUNT(*) as count
FROM event_stage_table
GROUP BY page
ORDER BY count DESC;
```

yields the following result

```
[('NextSong', 6820)
('Home', 806)
('Login', 92)
('Logout', 90)
('Downgrade', 60)
('Settings', 56)
('Help', 47)
('About', 36)
('Upgrade', 21)
('Save Settings', 10)
('Error', 9)
('Submit Upgrade', 8)
('Submit Downgrade', 1)]
```