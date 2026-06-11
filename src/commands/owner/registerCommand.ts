import client from "../../index.js";
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { SlashCommandBuilder, ChatInputCommandInteraction, REST, Routes, EmbedBuilder } from "discord.js";

// 1. Rekonstruksi __dirname untuk kompatibilitas Build/Docker
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
    data: new SlashCommandBuilder()
    .setName('sync')
    .setDescription('sync commands dengan discord, local atau global')
    .addStringOption(Option => 
        Option.setName('target')
        .setDescription('Pilih scope untuk sinkronisasi')
        .addChoices({
            name: 'Global',
            value: 'global'
        }, {
            name: 'Guild',
            value: 'guild'
        })
    ),
    scope: 'guild',
    async execute(interaction: ChatInputCommandInteraction) {
        try {
            
            if (interaction.user.id !== process.env.OWNER_ID) {
                await interaction.reply({
                    content: 'Lau siape mpruy? Cuma owner yang bisa pake command ini.',
                    flags: 'Ephemeral'
                    });
                return;
            }

            await interaction.deferReply({ flags: 'Ephemeral' });
            
            const target = interaction.options.getString('target');
            const commandsToSync: any[] = [];

            // 2. Gunakan __dirname untuk path yang dinamis (Asumsi file ini ada di dalam sub-folder commands/utils/)
            // Jika file ini ada langsung di dalam folder commands, ganti '..' menjadi '.'
            const commandsPath = path.join(__dirname, '..'); 
            
            // 3. Filter ketat: Blokir file .d.ts
            const commandFiles = fs.readdirSync(commandsPath, { recursive: true }).filter(file => {
                const fileName = String(file);
                return (fileName.endsWith('.ts') || fileName.endsWith('.js')) && !fileName.endsWith('.d.ts');
            });
            
            await interaction.editReply({ content: `Sedang sinkronisasi ${target} commands...` });
            
            for (const file of commandFiles) {
                const filePath = path.join(commandsPath, String(file));
                
                // 4. Konversi path ke URL absolute untuk ES Modules
                const fileUrl = new URL(`file://${filePath}`).href;
                const commandModule = await import(fileUrl);
                const command = commandModule.default;

                if (command && 'data' in command) {
                    // Memfilter command mana yang akan dimasukkan ke dalam array
                    const commandScope = command.scope || 'global'; // default global jika tidak ditulis
                    
                    if (target === 'guild') {
                        commandsToSync.push(command.data.toJSON());
                    } else if (target === 'global' && commandScope === 'global') {
                        commandsToSync.push(command.data.toJSON());
                    }
                }
            }

            // 5. Bersihkan spasi ambigu dari Token
            const cleanToken = process.env.DISCORD_BOT_TOKEN?.trim() || '';
            const rest = new REST({ version: '10' }).setToken(cleanToken);

            try {
                if (target === 'guild') {
                    await rest.put(
                        Routes.applicationGuildCommands(interaction.client.user!.id, interaction.guildId!),
                        { body: commandsToSync }
                    )
                } else {
                    await rest.put(
                        Routes.applicationCommands(process.env.CLIENT_ID!),
                        { body: commandsToSync }
                    );
                }

                //#region Embed Builder For list Command
                const commandList = commandsToSync.map(cmd => `\`/${cmd.name}\``).join(', ');
                const successEmbed = new EmbedBuilder()
                    .setColor('#00ff00') // Warna hijau neon penanda sukses
                    .setTitle('✅ Sinkronisasi Berhasil!')
                    .setDescription(`Berhasil melakukan sinkronisasi **${commandsToSync.length}** *${target}* commands ke Discord API.`)
                    .addFields(
                        { 
                            name: 'Daftar Commands', 
                            value: commandsToSync.length > 0 ? commandList : 'Tidak ada command yang disinkronisasi.' 
                        }
                    )
                    .setTimestamp() // Menambahkan waktu saat ini di bagian bawah embed
                    .setFooter({ text: `${client.user?.username} System` });

                await interaction.editReply({ embeds: [successEmbed] });
                //#endregion

            } catch (error) {
                console.error(error);
                await interaction.editReply({ content: 'Terjadi kesalahan saat sinkronisasi commands.' });
            }
            
        } catch (error) {
            console.error('Error executing sync command:', error);
        }
    }
}