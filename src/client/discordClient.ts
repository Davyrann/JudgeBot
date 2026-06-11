import { Client, Collection, GatewayIntentBits } from "discord.js";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from 'node:url';

// 1. Rekonstruksi __dirname untuk ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class DiscordClient extends Client {
    public applicationCommands: Collection<string, any>;
    
    constructor() {
        super({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent,
                GatewayIntentBits.GuildMembers,
            ]
        });
        this.applicationCommands = new Collection();
    }

    public async loadCommands() {
        // 2. Gunakan __dirname relatif. 
        // Asumsi: File ini ada di 'src/structures/DiscordClient.ts', 
        // jadi kita mundur 1 folder ('..') lalu masuk ke 'commands'
        const commandsPath = path.join(__dirname, '..', 'commands');
        const commandFiles = fs.readdirSync(commandsPath, { recursive: true }).filter(file => {
            const fileName = String(file);
            // ✅ Tambahkan syarat BUKAN .d.ts
            return (fileName.endsWith('.ts') || fileName.endsWith('.js')) && !fileName.endsWith('.d.ts');
        });

        console.log(`⏳ Memuat ${commandFiles.length} commands dari ${commandsPath}...`);

        for (const file of commandFiles) {
            const filePath = path.join(commandsPath, String(file));
            const fileUrl = new URL(`file://${filePath}`).href;
            
            const commandModule = await import(fileUrl);
            const command = commandModule.default;

            if (command && 'data' in command && 'execute' in command) {
                this.applicationCommands.set(command.data.name, command);
            }
        }
        console.log('✅ Semua commands berhasil dimuat ke memori!');
    }

    public async loadEvents() {
        // Sama seperti commands, arahkan path relatif menggunakan __dirname
        const eventsPath = path.join(__dirname, '..', 'events');
        const eventFiles = fs.readdirSync(eventsPath).filter(file => {
            const fileName = String(file);
            // ✅ Tambahkan syarat BUKAN .d.ts
            return (fileName.endsWith('.ts') || fileName.endsWith('.js')) && !fileName.endsWith('.d.ts');
        });
        console.log(`⏳ Memuat ${eventFiles.length} events dari ${eventsPath}...`);

        for (const file of eventFiles) {
            const filePath = path.join(eventsPath, String(file));
            const fileUrl = new URL(`file://${filePath}`).href;
            
            const eventModule = await import(fileUrl);
            const event = eventModule.default;

            if (event && 'name' in event && 'execute' in event) {
                if (event.once) {
                    this.once(event.name, (...args) => event.execute(...args));
                } else {
                    this.on(event.name, (...args) => event.execute(...args));
                }
            }
        }
        console.log('✅ Semua events berhasil dimuat ke memori!');
    }

    connect = async () => {
        try {
            // 3. Urutan Eksekusi Diperbaiki: Load dulu, baru Login!
            await this.loadCommands();
            await this.loadEvents();

            console.log('⏳ Connecting to Discord...');
            
            // Tambahkan .trim() untuk berjaga-jaga dari spasi ambigu di .env
            const token = process.env.DISCORD_BOT_TOKEN?.trim();
            await this.login(token);
            
            // Event ClientReady nanti yang akan menampilkan log "Bot Online"

        } catch (error) {
            // 4. Tampilkan error agar tidak kebingungan
            console.error('❌ Gagal menyalakan bot:', error);
        }
    }
}

export default DiscordClient;