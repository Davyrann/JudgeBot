-- AlterTable
ALTER TABLE "guild_settings" ADD COLUMN     "isLeaverActive" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "leaverChannelId" TEXT,
ADD COLUMN     "leaverEmbedImageUrl" TEXT,
ADD COLUMN     "leaverMessage" TEXT;
