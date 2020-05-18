import services


class dbstuff:
    def __init__(self, bot):
        self.bot = bot

    async def createTables(self, connection):
        await connection.execute('''
        create table if not exists Counters
        (
            count serial not null primary key,
            name text not null,
            summoned_by bigint not null,
            summoned_at int not null
        );
        ''')

        await connection.execute(services.ActivityService.sql.createTable)
        await connection.execute(services.StarboardService.sql().createTable)
        await connection.execute(services.ConfigService.sql().createTable)
        await connection.execute(services.BanService.sql().createTable)
        await connection.execute(services.MuteService.sql().createTable)
        await connection.execute(services.WarningsService.sql().createTable)
        await connection.execute(services.TimersService.sql().createTable)
        await connection.execute(services.EmojiService.sql().createTable)

    async def init(self):
        async with self.bot.pool.acquire() as conn:
            await self.createTables(conn)

        return self.bot.pool
