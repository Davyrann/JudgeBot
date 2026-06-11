import { SlashCommandBuilder, ChatInputCommandInteraction } from "discord.js";

export default {
    data: new SlashCommandBuilder().setName('ping').setDescription('Cek latency bot'),
    scope: 'global',
    async execute(interaction: ChatInputCommandInteraction) {
        try {
            const sent = await interaction.reply('Pinging...').then((response) => {
                return response;
            })
            await interaction.editReply(`Pong! Latency: ${sent.createdTimestamp - interaction.createdTimestamp}ms`);
        } catch (error) {
            await interaction.reply('Terjadi kesalahan saat menjalankan command ping.');
            console.error('Error executing ping command:', error);
        }
    }
}