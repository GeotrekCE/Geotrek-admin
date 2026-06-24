import { Dexie, type EntityTable } from "dexie"
import type {
  AppSyncSchemaProps,
  SettingsSchemaProps,
} from "@/schemas/settings"
import type {
  CommonReferencesSchemaProps,
  InfrastructureReferencesSchemaProps,
  InterventionReferencesSchemaProps,
  ReportReferencesSchemaProps,
  SignageReferencesSchemaProps,
} from "@/schemas/references"
import type {
  InfrastructureDataSchemaProps,
  InterventionDataSchemaProps,
  ReportDataSchemaProps,
  SignageDataSchemaProps,
} from "@/schemas/data"

const DB_NAME = "gtam"
Dexie.debug = true

export const db = new Dexie(DB_NAME) as Dexie & {
  settings: EntityTable<SettingsSchemaProps & { id: string }, "id">
  appSync: EntityTable<AppSyncSchemaProps, "id">
  references: EntityTable<
    (
      | CommonReferencesSchemaProps
      | SignageReferencesSchemaProps
      | InfrastructureReferencesSchemaProps
      | InterventionReferencesSchemaProps
      | ReportReferencesSchemaProps
    ) & {
      id: string
    },
    "id"
  >
  signageData: EntityTable<SignageDataSchemaProps & { sync?: boolean }>
  infrastructureData: EntityTable<
    InfrastructureDataSchemaProps & { sync?: boolean }
  >
  interventionData: EntityTable<
    InterventionDataSchemaProps & { sync?: boolean }
  >
  reportData: EntityTable<ReportDataSchemaProps & { sync?: boolean }>
}

db.version(1).stores({
  settings: "id",
  appSync: "id",
  references: "id",
  signageData: "++id, name, description",
  infrastructureData: "++id, name, description",
  interventionData: "++id, name, description",
  reportData: "++id",
})
