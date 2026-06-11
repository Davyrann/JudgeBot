-- AlterTable
ALTER TABLE "guild_settings" ADD COLUMN     "isAutoResponderActive" BOOLEAN NOT NULL DEFAULT false;

-- CreateTable
CREATE TABLE "auto_responder" (
    "id" TEXT NOT NULL,
    "guildID" TEXT NOT NULL,
    "trigger" TEXT NOT NULL,
    "response" TEXT NOT NULL,

    CONSTRAINT "auto_responder_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "auto_responder" ADD CONSTRAINT "auto_responder_guildID_fkey" FOREIGN KEY ("guildID") REFERENCES "guild_settings"("guildID") ON DELETE RESTRICT ON UPDATE CASCADE;
