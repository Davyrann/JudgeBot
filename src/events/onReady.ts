import { Events } from "discord.js";

export default {
    name: Events.ClientReady,
    once: true,
    async execute(client: any) {
        console.log('================================');
        console.log(`Running on ${process.platform} ${process.arch}`);
        console.log(`Node.js version: ${process.version}`);
        console.log(`Memory Usage: ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB / ${(process.memoryUsage().heapTotal / 1024 / 1024).toFixed(2)} MB`);
        console.log('================================');
        console.log(`Logged in as ${client.user?.username}!`);
    }
};