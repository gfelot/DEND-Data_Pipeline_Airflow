class SqlQueries:
    create_staging_events_table = ("""
                DROP TABLE IF EXISTS staging_events; 
                CREATE TABLE IF NOT EXISTS staging_events (
                    artist varchar(256),
                    auth varchar(256),
                    firstName varchar(256),
                    gender varchar(256),
                    item_in_session int4,
                    lastName varchar(256),
                    length numeric(18,0),
                    level varchar(256),
                    location varchar(256),
                    method varchar(256),
                    page varchar(256),
                    registration numeric(18,0),
                    sessionId int4,
                    song varchar(256),
                    status int4,
                    ts int8,
                    userAgent varchar(256),
                    userId int4
                );
            """)

    create_staging_songs_table = ("""
                DROP TABLE IF EXISTS staging_songs;
                CREATE TABLE IF NOT EXISTS staging_songs (
                    num_songs int4,
                    artist_id varchar(256),
                    artist_name varchar(256),
                    artist_latitude numeric(18,0),
                    artist_longitude numeric(18,0),
                    artist_location varchar(256),
                    song_id varchar(256),
                    title varchar(256),
                    duration numeric(18,0),
                    year int4
                );
            """)

    create_songplays_table = ("""
                DROP TABLE IF EXISTS songplays;
                CREATE TABLE IF NOT EXISTS songplays (
                    play_id varchar(32) NOT NULL,
                    start_time timestamp NOT NULL,
                    user_id int4 NOT NULL,
                    level varchar(256),
                    song_id varchar(256),
                    artist_id varchar(256),
                    session_id int4,
                    location varchar(256),
                    user_agent varchar(256),
                    CONSTRAINT songplays_pkey PRIMARY KEY (play_id)
                );
             """)

    insert_songplay_table = ("""
        SELECT  md5(events.sessionid || events.start_time) songplay_id,
                events.start_time, 
                events.user_id, 
                events.level, 
                songs.song_id, 
                songs.artist_id, 
                events.session_id, 
                events.location, 
                events.useragent
        FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
                FROM staging_events
                WHERE page='NextSong') events
        LEFT JOIN staging_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
    """)

    create_users_table = ("""
            DROP TABLE IF EXISTS users;
            CREATE TABLE IF NOT EXISTS users (
                user_id int4 NOT NULL,
                first_name varchar(256),
                last_name varchar(256),
                gender varchar(256),
                level varchar(256),
                CONSTRAINT users_pkey PRIMARY KEY (userid)
            );
        """)

    insert_user_table = ("""
        SELECT distinct user_id, firstName, lastName, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """)

    create_songs_table = ("""
            DROP TABLE IF EXISTS songs;
            CREATE TABLE IF NOT EXISTS songs (
                song_id varchar(256) NOT NULL,
                title varchar(256),
                artist_id varchar(256),
                year int4,
                duration numeric(18,0),
                CONSTRAINT songs_pkey PRIMARY KEY (songid)
            );
        """)

    insert_song_table = ("""
        SELECT distinct song_id, title, artist_id, year, duration
        FROM staging_songs
    """)

    create_artists_table = ("""
            DROP TABLE IF EXISTS artists;
            CREATE TABLE IF NOT EXISTS artists (
                artist_id varchar(256) NOT NULL,
                name varchar(256),
                location varchar(256),
                latitude numeric(18,0),
                longitude numeric(18,0)
            );
        """)

    insert_artist_table = ("""
        SELECT distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """)

    create_times_table = ("""
            DROP TABLE IF EXISTS time;
            CREATE TABLE IF NOT EXISTS time (
                start_time timestamp NOT NULL,
                hour int4,
                day int4 NOT NULL,
                week int4 ,
                month int4 NOT NULL,
                year int4 NOT NULL,
                weekday int4,
                PRIMARY KEY(start_time, day, month, year));
        """)

    insert_time_table = ("""
        SELECT start_time, extract(hour from start_time), extract(day from start_time), extract(week from start_time), 
               extract(month from start_time), extract(year from start_time), extract(dayofweek from start_time)
        FROM songplays
    """)
