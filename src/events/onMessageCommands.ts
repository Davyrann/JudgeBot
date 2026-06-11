import fs from "node:fs";
import path from "node:path";
import { Events, Message, REST, Routes, EmbedBuilder } from "discord.js";

export default {
    name: Events.MessageCreate,
    once: false,
    async execute(message: Message) {
        
        if (message.author.bot || !message.guild) return;

        if (message.content.startsWith(`${process.env.PREFIX}sync`)) {
            if (message.author.id !== process.env.OWNER_ID) return;

            const args = message.content.split(' ');
            const target = args[1];

            // Validasi input
            if (!target || (target !== 'global' && target !== 'guild')) {
                await message.reply('❌ Format salah! Gunakan: `!sync global` atau `!sync guild`');
                return;
            }

            const loadingMessage = await message.reply('🔄 Sedang memproses sinkronisasi API...');

            const commandsToSync: any[] = [];
            const commandsPath = path.join(process.cwd(), 'src', 'commands');
            
            try {
                const commandFiles = fs.readdirSync(commandsPath, { recursive: true }).filter(file => { 
                    const fileName = String(file); 
                    return fileName.endsWith('.ts') || fileName.endsWith('.js');
                });

                for (const file of commandFiles) {
                    const filePath = path.join(commandsPath, String(file));
                    const commandModule = await import(filePath);
                    const command = commandModule.default;
                   
                    if (command && 'data' in command) {
                        const commandScope = command.scope || 'global';
                        if (target === 'guild') {
                            commandsToSync.push(command.data.toJSON());
                        } else if (target === 'global' && commandScope === 'global') {
                            commandsToSync.push(command.data.toJSON());
                        }
                    }
                }

                const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_BOT_TOKEN!);

                if (target === 'global') {
                    await rest.put(
                        Routes.applicationCommands(process.env.CLIENT_ID!),
                        { body: commandsToSync }
                    );
                } else {
                    await rest.put(
                        Routes.applicationGuildCommands(process.env.CLIENT_ID!, message.guild.id),
                        { body: commandsToSync }
                    );
                }

                const commandList = commandsToSync.map(cmd => `\`/${cmd.name}\``).join(', ');
                
                const successEmbed = new EmbedBuilder()
                    .setColor('#00ff00')
                    .setTitle('✅ Sinkronisasi Berhasil!')
                    .setDescription(`Berhasil melakukan sinkronisasi **${commandsToSync.length}** *${target}* commands ke Discord API.`)
                    .addFields(
                        { 
                            name: 'Daftar Commands', 
                            value: commandsToSync.length > 0 ? commandList : 'Tidak ada command yang disinkronisasi.' 
                        }
                    )
                    .setTimestamp()
                    .setFooter({ text: 'JudgeBot System' });

                await loadingMessage.edit({ content: '', embeds: [successEmbed] });

            } catch (error) {
                console.error('Error saat sync:', error);
                await loadingMessage.edit('❌ Terjadi kesalahan saat mencoba sinkronisasi API. Cek console log.');
            }
        }
    }
}