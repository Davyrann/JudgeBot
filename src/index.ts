import "dotenv/config";
import DiscordClient from "./client/discordClient.js";

const client = new DiscordClient();

async function main() {
    try {
        
        await client.connect();
        
    } catch (error) {
        console.error('Error occurred while starting the bot:', error);
    }
}

main();

export default client;