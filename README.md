
```
JudgeBot
├─ .dockerignore
├─ .prettierrc
├─ Dockerfile
├─ generated
│  └─ prisma
│     ├─ browser.ts
│     ├─ client.ts
│     ├─ commonInputTypes.ts
│     ├─ enums.ts
│     ├─ internal
│     │  ├─ class.ts
│     │  ├─ prismaNamespace.ts
│     │  └─ prismaNamespaceBrowser.ts
│     ├─ models
│     │  ├─ AutoResponder.ts
│     │  └─ GuildSetting.ts
│     └─ models.ts
├─ package.json
├─ pnpm-lock.yaml
├─ pnpm-workspace.yaml
├─ prisma
│  ├─ migrations
│  │  ├─ 20260611031913_init
│  │  │  └─ migration.sql
│  │  ├─ 20260611032954_add_welcome_embed_image_url
│  │  │  └─ migration.sql
│  │  ├─ 20260611033104_add_leave_messager
│  │  │  └─ migration.sql
│  │  ├─ 20260611043601_add_auto_responder
│  │  │  └─ migration.sql
│  │  └─ migration_lock.toml
│  └─ schema.prisma
├─ prisma.config.ts
├─ src
│  ├─ commands
│  │  ├─ owner
│  │  │  └─ registerCommand.ts
│  │  └─ utils
│  │     └─ pingCommand.ts
│  ├─ database
│  │  └─ prismaClient.ts
│  ├─ events
│  │  ├─ onMemberAdd.ts
│  │  ├─ onMemberRemove.ts
│  │  ├─ onMessage.ts
│  │  ├─ onMessageCommands.ts
│  │  └─ onReady.ts
│  └─ index.ts
└─ tsconfig.json

```