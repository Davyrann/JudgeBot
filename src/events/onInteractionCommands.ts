import { Events, type Interaction } from 'discord.js';
import client from '../index.js'; // Pastikan import client ini mengarah ke file index kamu

export default {
    name: Events.InteractionCreate,
    once: false,
    async execute(interaction: Interaction) {
        
        // 1. Abaikan jika ini bukan slash command (misal interaksi tombol/menu)
        if (!interaction.isChatInputCommand()) return;

        // 2. Cari file command di memori bot berdasarkan nama yang diketik user
        // (Pastikan kamu sudah memasukkan command ke client.commands di index.ts)
        const command = client.applicationCommands.get(interaction.commandName);

        if (!command) {
            console.error(`Tidak ada command yang cocok dengan nama /${interaction.commandName}.`);
            return;
        }

        try {
            // 3. Eksekusi fungsi 'execute' yang ada di dalam file sync.ts tadi!
            await command.execute(interaction);
        } catch (error) {
            console.error(`Error saat mengeksekusi /${interaction.commandName}:`, error);
            
            // 4. Fallback jika terjadi error agar bot tidak "thinking" selamanya di Discord
            if (interaction.replied || interaction.deferred) {
                await interaction.followUp({ content: '❌ Terjadi kesalahan saat menjalankan perintah ini!', flags: 'Ephemeral' });
            } else {
                await interaction.reply({ content: '❌ Terjadi kesalahan saat menjalankan perintah ini!', flags: 'Ephemeral' });
            }
        }
    }
}