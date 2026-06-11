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
  | InfrastructureDataSchemaProps[0]
  | SignageDataSchemaProps[0]
  | InterventionDataSchemaProps[0]
  | (ReportDataSchemaProps[0] & { name: string })
) & { pictogram: { url?: string }; reference: string }

export const infrastructureDataSchema = z.array(
  z.object({
    id: z.number().int().positive(),
    date_insert: z.string(),
    date_update: z.string(),
    api_geom: z.object({
      type: z.string().min(1),
      coordinates: z.array(z.number()),
    }),
    published: z.boolean(),
    name: z.string().min(1, "Le nom est obligatoire"),
    description: z.string(),
    implantation_year: z.union([z.number(), z.null()]),
    accessibility: z.string(),
    structure: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
    access: z.null(),
    type: z.object({
      id: z.number().int().positive({ message: "Le type est obligatoire" }),
      name: z.string().min(1),
    }),
    maintenance_difficulty: z.null(),
    usage_difficulty: z.null(),
    conditions: z.array(
      z.object({
        id: z.number().int().positive(),
        name: z.string().min(1),
      })
    ),
  })
)

export const signageDataSchema = z.array(
  z.object({
    id: z.number().int().positive(),
    api_geom: z.object({
      type: z.string().min(1),
      coordinates: z
        .array(z.number())
        .length(2, "Les coordonnées sont obligatoires"),
    }),

    structure: z
      .object({
        id: z.number().int(),
        name: z.string(),
      })
      .refine((data) => !!data.name, "La structure est obligatoire"),

    date_insert: z.string(),
    date_update: z.string(),
    published: z.boolean(),
    name: z.string().min(1, "Le nom est obligatoire"),
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
        name: z.string().min(1),
      })
      .refine((data) => !!data.name, "Le type est obligatoire"),
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
        direction: z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
        type: z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
        color: z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
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
            text: z.string().min(1),
            distance: z.string().min(1),
            time: z.string().min(1),
          })
        ),
      })
    ),
  })
)

export const interventionDataSchema = z.array(
  z.object({
    id: z.number().int().positive(),
    api_geom: z.object({
      type: z.string().min(1),
      coordinates: z.array(z.number()),
    }),
    name: z.string().min(1, "Le nom est obligatoire"),
    date_insert: z.string(),
    date_update: z.string(),
    begin_date: z.string(),
    end_date: z.string(),
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
    stake: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
    status: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
    type: z
      .object({
        id: z.number().int().positive(),
        name: z.string().min(1),
      })
      .refine((data) => data, "Le type est obligatoire"),
    disorders: z.array(
      z.object({
        id: z.number().int().positive(),
        name: z.string(),
      })
    ),
    man_day: z.array(
      z.object({
        id: z.number().int().positive(),
        nb_days: z.string().min(1),
        job: z.object({
          id: z.number().int().positive(),
          name: z.string().min(1),
        }),
      })
    ),
    description: z.string(),
    access: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
  })
)

export const reportDataSchema = z.array(
  z.object({
    id: z.number().int().positive(),
    date_insert: z.string(),
    date_update: z.string(),
    email: z.string(),
    comment: z.string(),
    api_geom: z.object({
      type: z.string().min(1),
      coordinates: z.array(z.number()),
    }),
    activity: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
    category: z.object({
      id: z.number().int().positive(),
      name: z.string().min(1),
    }),
    problem_magnitude: z.object({
      id: z.number().int().positive(),
      name: z.string(),
    }),
    status: z.null(),
  })
)
