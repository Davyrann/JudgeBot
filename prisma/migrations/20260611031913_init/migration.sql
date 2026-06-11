-- CreateTable
CREATE TABLE "guild_settings" (
    "id" TEXT NOT NULL,
    "guildID" TEXT NOT NULL,
    "welcomeChannelId" TEXT,
    "welcomeMessage" TEXT,
    "isWelcomeActive" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "guild_settings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "guild_settings_guildID_key" ON "guild_settings"("guildID");
