import * as z from "zod"

export type SettingsSchemaProps = z.infer<typeof settingsSchema>
export type AppSyncSchemaProps = z.infer<typeof appSync>

export const settingsSchema = z.object({
  settings: z.object({
    intervalSyncInHours: z.object({
      data: z.number().int().positive(),
      references: z.number().int().positive(),
    }),
    map: z.object({
      layers: z.object({
        online: z.object({
          base_layers: z.array(
            z.object({
              name: z.string().min(1),
              slug: z.string().min(1),
              url: z.string(),
            })
          ),
        }),
        offline: z.array(
          z.object({
            id: z.number().int().positive(),
            pmtiles_url: z.string(),
            json_style_url: z.string(),
            name: z.string().min(1),
            "content-length": z.number().int().positive(),
            options: z.object({
              attribution: z.string(),
              center: z.array(z.number()),
              maxBounds: z.array(z.array(z.number())),
              maxZoom: z.number().int().positive(),
              minZoom: z.number().int(),
              zoom: z.number().int(),
            }),
          })
        ),
      }),
      localOptions: z.object({
        bounds: z.array(z.number()).length(4),
      }),
    }),
    appOptions: z.object({
      minZoom: z.number().int(),
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
      is_superuser: z.boolean(),
      can_bypass_structure: z.boolean(),
    }),
    userName: z.string().min(1),
  }),
})

export const appSync = z.object({
  id: z.string(),
  lastSync: z.string(),
  bounds: z.array(z.number()).length(4).optional(),
  structure: z.union([z.null(), z.number()]).optional(),
  map: z
    .object({
      layers: z.array(z.string()),
    })
    .optional(),
})
