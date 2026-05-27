import * as z from "zod"

export type SettingsSchemaProps = z.infer<typeof settingsSchema>
export type AppConfigSchemaProps = z.infer<typeof appConfig>

export const settingsSchema = z.object({
  settings: z.object({
    intervalSyncInHours: z.object({
      references: z.number().int().positive(),
    }),
    maps: z.object({
      layers: z.array(
        z.object({
          pmtiles_url: z.string(),
          json_style_url: z.string(),
          name: z.string().min(1),
          options: z.object({
            attribution: z.string().min(1),
            center: z.array(z.number().positive()),
            maxBounds: z.array(z.array(z.number().positive())),
            maxZoom: z.number().int().positive(),
            minZoom: z.number().int(),
            zoom: z.number().int(),
          }),
        })
      ),
      localOptions: z.object({
        minZoom: z.number().int(),
      }),
    }),
  }),
  user: z.object({
    attachedStructure: z.object({
      id: z.number().int().positive(),
      label: z.string().min(1),
    }),
    firstName: z.string(),
    lastName: z.string(),
    permissions: z.object({
      signage: z.object({
        create: z.boolean(),
        update_geom: z.boolean(),
        update: z.boolean(),
        delete: z.boolean(),
        read: z.boolean(),
      }),
      infrastructure: z.object({
        create: z.boolean(),
        update_geom: z.boolean(),
        update: z.boolean(),
        delete: z.boolean(),
        read: z.boolean(),
      }),
      intervention: z.object({
        create: z.boolean(),
        update_geom: z.boolean(),
        update: z.boolean(),
        delete: z.boolean(),
        read: z.boolean(),
      }),
      report: z.object({
        create: z.boolean(),
        update_geom: z.boolean(),
        update: z.boolean(),
        delete: z.boolean(),
        read: z.boolean(),
      }),
    }),
    userName: z.string().min(1),
  }),
})

export const appConfig = z.object({
  syncReferences: z.object({
    lastSync: z.string(),
  }),
  syncData: z.object({
    bounds: z.array(z.number()).length(4),
    structure: z.union([z.null(), z.number()]),
    lastSync: z.string(),
  }),
  list: z.object({
    snapPointIndex: z.number(),
    scrollPosition: z.union([z.number(), z.null()]),
  }),
})
