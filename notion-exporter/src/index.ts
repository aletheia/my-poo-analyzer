import {Client} from '@notionhq/client'
import dotenv from 'dotenv'

void (async () => {
    dotenv.config();
    const client = new Client({ auth: process.env.NOTION_TOKEN });
    const databaseid = '1404e51c77c94fd39b4076d47ee2fa85'
    const response = await client.databases.query({
        database_id: databaseid,
    });
    
    console.log(response);

})();