import axios from "axios";
import { SlashCommandBuilder, ChatInputCommandInteraction, EmbedBuilder } from "discord.js";

export default {
    data: new SlashCommandBuilder()
    .setName('skin')
    .setDescription('Upload skin Minecraft kamu dan dapatkan previewnya!')
    .addAttachmentOption(option => 
        option.setName('gambar')
            .setDescription('Upload file gambar skin (wajib berformat .png)')
            .setRequired(true)
    )
    .addStringOption(option => 
        option.setName('name')
            .setDescription('Beri nama untuk skin ini (Opsional)')
            .setRequired(false)
    )
    .addStringOption(option => 
        option.setName('variant')
            .setDescription('Pilih model karakter')
            .setRequired(false)
            .addChoices(
                { name: 'Classic (Steve)', value: 'classic' },
                { name: 'Slim (Alex)', value: 'slim' }
            )
    ),
    scope: 'global',
    async execute(interaction: ChatInputCommandInteraction) {
        // Karena API eksternal butuh waktu, gunakan deferReply agar tidak timeout
        await interaction.deferReply();

        // 2. Mengambil input dari pengguna
        const attachment = interaction.options.getAttachment('gambar');
        const skinName = interaction.options.getString('name') || `${interaction.user.username}'s Skin`;
        const variant = interaction.options.getString('variant') || 'classic';

        // Validasi: Pastikan yang diunggah benar-benar gambar
        if (!attachment || !attachment.contentType?.startsWith('image/')) {
            await interaction.editReply('❌ Format salah! Harap unggah file gambar (.png).');
            return;
        }

        try {
            // 3. Menembak API MineSkin dengan Axios
            // Menggunakan method post langsung agar kode lebih bersih dari Axios config object
            const response = await axios.post('https://api.mineskin.org/v2/generate', {
                variant: variant,
                name: skinName,
                visibility: "public",
                // Ajaibnya di sini: Kita langsung lempar URL gambar dari server Discord!
                url: attachment.url 
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    // Pastikan kamu menambahkan MINESKIN_TOKEN di file .env kamu!
                    'Authorization': `Bearer ${process.env.MINESKIN_TOKEN}` 
                }
            });

            // Mendapatkan data dari response
            const skinData = response.data;

            // Mengambil UUID langsung dari object skin (jauh lebih aman daripada memotong link)
            const skinUuid = skinData.skin.uuid;
            const textureUrl = skinData.skin.texture.url.skin;
            const isSlim = skinData.skin.variant === 'slim'; // Menghasilkan true atau false
            const encodedTexture = encodeURIComponent(textureUrl);
            // Merakit URL publik MineSkin
            
            const mineskinUrl = `https://mineskin.org/skins/${skinUuid}`;
            const render3dUrl = `https://render.mineskin.org/render?overlay=true&body=true&scale=50&slim=${isSlim}&url=${encodedTexture}`;
            // Membangun Embed Hasil
            const resultEmbed = new EmbedBuilder()
                .setColor('Green')
                .setTitle('Skin Berhasil Dibuat!')
                // Menambahkan link yang bisa diklik langsung pada teks deskripsi
                .setDescription(`Skin **${skinName}** telah berhasil digenerate.\n[**Klik di sini untuk melihat Preview Skin**](${mineskinUrl})`)
                .setThumbnail(attachment.url)
                .setImage(render3dUrl)
                .addFields(
                    { name: '_Skin Set Command_', value: `/skin set ${mineskinUrl}`, inline: false },
                )
                .setFooter({ text: 'Skin set Generator | MineSkin', iconURL: 'https://ccvaults.com/assets/10.%20Items/23.%20Flowers/Seagrass.png' })
                .setTimestamp();

            await interaction.editReply({ embeds: [resultEmbed] });

        } catch (error: any) {
            console.error('Error saat request ke MineSkin:', error.response?.data || error.message);
            
            // Mengambil pesan error dari API jika ada
            const apiError = error.response?.data?.message || 'Terjadi kesalahan internal pada bot.';
            
            await interaction.editReply(`❌ **Gagal membuat skin!**\nAlasan: \`${apiError}\``);
        }
    }
}