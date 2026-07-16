import { m } from "@/paraglide/messages"
import * as z from "zod"

export type InfrastructureDataSchemaProps = z.infer<
  typeof infrastructureDataSchema
>
export type SignageDataSchemaProps = z.infer<typeof signageDataSchema>

export type InterventionDataSchemaProps = z.infer<typeof interventionDataSchema>
export type ReportDataSchemaProps = z.infer<typeof reportDataSchema>

export type DataSchemapProps = {
  infrastructure: InfrastructureDataSchemaProps
  signage: SignageDataSchemaProps
}

export type DataSchemaPropsMixed = (
  | InfrastructureDataSchemaProps
  | SignageDataSchemaProps
  | InterventionDataSchemaProps
  | (ReportDataSchemaProps & { name: string })
) & { pictogram: { url?: string }; reference: string }

const pointGeomSchema = z
  .object({
    type: z.literal("Point"),
    coordinates: z.array(z.number()),
  })
  .refine(
    (data) => data.coordinates.length === 2,
    m["form.location-required"]()
  )

const lineStringGeomSchema = z.object({
  type: z.literal("LineString"),
  coordinates: z
    .array(z.array(z.number()).length(2, m["form.location-required"]()))
    .min(2, m["form.location-required"]()),
})

const multiLineStringGeomSchema = z.object({
  type: z.literal("MultiLineString"),
  coordinates: z
    .array(
      z
        .array(z.array(z.number()).length(2, m["form.location-required"]()))
        .min(2, m["form.location-required"]())
    )
    .min(1, m["form.location-required"]()),
})

export const geometrySchema = z.discriminatedUnion("type", [
  pointGeomSchema,
  lineStringGeomSchema,
  multiLineStringGeomSchema,
])

export const infrastructureDataSchema = z.object({
  id: z.number().int().positive(),
  date_insert: z.string(),
  date_update: z.string(),
  geom: z.union([z.null(), geometrySchema]),
  name: z.string().min(1, m["form.name-required"]()),
  description: z.string(),
  implantation_year: z.union([z.number(), z.null()]),
  accessibility: z.string(),
  structure: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.structure-required"]()),
  access: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  type: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.type-required"]()),
  maintenance_difficulty: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  usage_difficulty: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  conditions: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  appSynced: z.boolean().optional(),
  appNewItem: z.boolean().optional(),
})

export const signageDataSchema = z.object({
  id: z.number().int().positive(),
  geom: z.union([z.null(), geometrySchema]),
  structure: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.structure-required"]()),
  date_insert: z.string(),
  date_update: z.string(),
  name: z.string().min(1, m["form.name-required"]()),
  description: z.string(),
  implantation_year: z.union([z.number(), z.null()]),
  code: z.string(),
  printed_elevation: z.union([z.number(), z.null()]),
  access: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  manager: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  sealing: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  type: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.type-required"]()),
  conditions: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  blades: z.array(
    z.object({
      id: z.number().int().positive(),
      number: z.string().min(1),
      direction: z.union([
        z.null(),
        z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
      ]),
      type: z.object({
        id: z.number().int().positive(),
        name: z.string().min(1),
      }),
      color: z.union([
        z.null(),
        z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
      ]),
      conditions: z.array(
        z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        })
      ),
      lines: z.array(
        z.object({
          id: z.number().int().positive(),
          number: z.number().int().positive(),
          text: z.string(),
          distance: z.union([z.null(), z.string().min(1)]),
          time: z.union([z.null(), z.string().min(1)]),
        })
      ),
    })
  ),
  appSynced: z.boolean().optional(),
  appNewItem: z.boolean().optional(),
})

export const interventionDataSchema = z.object({
  id: z.number().int().positive(),
  geom: z.union([z.null(), geometrySchema]),
  structure: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.structure-required"]()),
  name: z.string().min(1, m["form.name-required"]()),
  date_insert: z.string(),
  date_update: z.string(),
  begin_date: z.string().min(1, m["form.begin-date-required"]()),
  end_date: z.union([z.null(), z.string()]),
  subcontracting: z.boolean(),
  width: z.number(),
  height: z.number(),
  material_cost: z.number().int(),
  heliport_cost: z.number().int(),
  contractor_cost: z.number().int(),
  contractors: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    })
  ),
  length: z.number(),
  stake: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
  ]),
  status: z
    .object({
      id: z.number().int(),
      name: z.string(),
    })
    .refine((data) => !!data.name, m["form.status-required"]()),
  type: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
  ]),
  disorders: z.array(
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    })
  ),
  man_day: z.array(
    z.object({
      nb_days: z.number(),
      job: z.object({
        id: z.number().int().positive(),
        name: z.string(),
      }),
    })
  ),
  description: z.string(),
  access: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  appSynced: z.boolean().optional(),
  appNewItem: z.boolean().optional(),
})

export const reportDataSchema = z.object({
  id: z.number().int().positive(),
  date_insert: z.string(),
  date_update: z.string(),
  email: z.string(),
  comment: z.string(),
  geom: z.union([z.null(), geometrySchema]),
  activity: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  category: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  problem_magnitude: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  status: z.union([
    z.null(),
    z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
  ]),
  appSynced: z.boolean().optional(),
  appNewItem: z.boolean().optional(),
})
