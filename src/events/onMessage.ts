import prisma from "../database/prismaClient.js";
import { Events, Message } from "discord.js";

export default {
    name: Events.MessageCreate,
    once: false,
    async execute(message: Message) {
        if (message.author.bot || !message.guild) return;
        if (message.author.bot) return;

        //#region AutoResponse
        const settings = await prisma.guildSetting.findUnique({
            where: {
                guildID: message.guild?.id || ""
            }
        });

        if (!settings || !settings.isAutoResponderActive) return;


        const autoResponse = await prisma.autoResponder.findFirst({
            where: {
                guildID: message.guild?.id || "",
                trigger: message.content
            }
        });

        if (autoResponse) {
            if (message.channel.isSendable()) {
                await message.channel.send(autoResponse.response);
            }
        }
    }
}