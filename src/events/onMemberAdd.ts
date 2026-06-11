import { EmbedBuilder, Events, GuildMember } from "discord.js";
import prisma from "../database/prismaClient.js";

export default {
    name: Events.GuildMemberAdd,
    once: false,
    async execute(member: GuildMember) {
        const settings = await prisma.guildSetting.findUnique({
        where: {
            guildID: member.guild.id
        }
    });

    if (!settings || !settings.isWelcomeActive || !settings.welcomeChannelId) return;

    const channel = member.guild.channels.cache.get(settings.welcomeChannelId);

    if (!channel || !channel.isTextBased()) return;

    const welcomeEmbed = new EmbedBuilder()
        .setTitle(`Welcome to ${member.guild.name}, ${member.user.username}!`)
        .setDescription(settings.welcomeMessage || "Selamat datang diserver kita, Kamu adalah member ke-" + member.guild.memberCount)
        .setThumbnail(member.user.displayAvatarURL())
        .setImage(settings.welcomeEmbedImageUrl || "https://i.imgur.com/bpywqIz.png")
        .setColor("Green")
        .setTimestamp()
        .setFooter({ text: "Member Joined!"});

    channel.send({ embeds: [welcomeEmbed] });
    }
}