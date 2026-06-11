import { EmbedBuilder, Events, GuildMember } from "discord.js";
import prisma from "../database/prismaClient.js";

export default {
    name: Events.GuildMemberRemove,
    once: false,
    async execute(member: GuildMember) {
        const settings = await prisma.guildSetting.findUnique({
            where: {
                guildID: member.guild.id
            }
        });

        if (!settings || !settings.isLeaverActive || !settings.leaverChannelId) return;

        const channel = member.guild.channels.cache.get(settings.leaverChannelId);

        if (!channel || !channel.isTextBased()) return;

        const leaverEmbed = new EmbedBuilder()
            .setTitle(`Goodbye from ${member.guild.name}, ${member.user.username}!`)
            .setDescription(settings.leaverMessage || "Selamat tinggal dari server kita, Kamu adalah member ke-" + member.guild.memberCount)
            .setThumbnail(member.user.displayAvatarURL())
            .setImage(settings.leaverEmbedImageUrl || "https://i.imgur.com/ZH1dTSy.png")
            .setColor("Blue")
            .setTimestamp()
            .setFooter({ text: "Member Left!"});

        channel.send({ embeds: [leaverEmbed] });
    }
}