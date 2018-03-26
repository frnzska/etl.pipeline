# (1)

SELECT user_id, count(1) as n_installs
FROM user_first_install_fact
WHERE date_sk = (select to_char(CURRENT_DATE - INTERVAL '1 day', 'YYYYMMDD'))
GROUP BY user_id
HAVING count(1) > 1;


# (2)

SELECT channel_name, count(1)
FROM user_first_install_fact user_install
	JOIN client_dim client
		USING (client_sk)
	JOIN channel_dim channel
		USING (channel_sk)
WHERE client.os_name like 'Android'
GROUP BY channel.channel_name
ORDER BY 2 DESC
LIMIT 5;
